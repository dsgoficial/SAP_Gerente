"""Disposable GeoPackage read cache. All authoritative writes stay in provider.py.

GDAL creates a standard empty GeoPackage; sqlite3 fills bounded pages and
maintains its RTree. QGIS opens its OGR provider with ForceReadOnly, so none
of the native provider's write methods can bypass the service coordinator.
"""
import sqlite3
import struct
import threading
import math
import json
from uuid import uuid4

from osgeo import ogr,osr
from qgis.core import Qgis,QgsDataProvider,QgsProviderRegistry

from . import values
from .provider import Cache,CACHE_DIRECTORY,PAGE_LIMIT


def quote(name):
    return '"'+name.replace('"','""')+'"'


class NativeCache(Cache):
    native=True

    def __init__(self,specs,geometry_type,z,srid):
        CACHE_DIRECTORY.mkdir(parents=True,exist_ok=True)
        self.path=str(CACHE_DIRECTORY/(uuid4().hex+'.gpkg'))
        self.specs=specs;self.srid=srid;self.has_geometry=geometry_type is not None
        self.signed_zero_fields=set()
        self.geometry_column='_dsg_geometry'
        names={s['name'].lower() for s in specs}
        while self.geometry_column.lower() in names:
            self.geometry_column += '_'
        self.rtree='rtree_features_'+self.geometry_column
        self.lock=threading.RLock()
        ds=ogr.GetDriverByName('GPKG').CreateDataSource(self.path)
        if ds is None:raise ValueError('Não foi possível criar o cache GeoPackage.')
        srs=osr.SpatialReference()
        if self.has_geometry:srs.ImportFromEPSG(srid)
        kind=ogr.wkbNone if not geometry_type else values.wkb_code(geometry_type,z)
        layer=ds.CreateLayer('features',srs if self.has_geometry else None,kind,options=['FID=fid','GEOMETRY_NAME='+self.geometry_column,'SPATIAL_INDEX=YES'])
        layer.CreateField(ogr.FieldDefn('dsg_id',ogr.OFTString))
        for spec in specs:
            kind=spec['kind']
            typ={'integer':ogr.OFTInteger64,'real':ogr.OFTReal,'boolean':ogr.OFTInteger,
                 'date':ogr.OFTDate,'bytes':ogr.OFTBinary}.get(kind,ogr.OFTString)
            if kind=='datetime' and (spec.get('precision') is None or spec['precision']<=3):typ=ogr.OFTDateTime
            definition=ogr.FieldDefn(spec['name'],typ)
            if kind=='boolean':definition.SetSubType(ogr.OFSTBoolean)
            if layer.CreateField(definition)!=ogr.OGRERR_NONE:raise ValueError('Campo de cache não criado: '+spec['name'])
        layer=None;ds=None
        self.db=sqlite3.connect(self.path,check_same_thread=False,isolation_level=None)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=NORMAL')
        # The cache is exclusively populated here, never edited by OGR. Its
        # spatial index is maintained in the same transaction as each page.
        for (name,) in self.db.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='features'").fetchall():
            self.db.execute('DROP TRIGGER '+quote(name))
        self.db.execute("UPDATE gpkg_ogr_contents SET feature_count=NULL WHERE table_name='features'")
        self.db.execute('CREATE TABLE ids(dsg_id TEXT PRIMARY KEY,fid INTEGER NOT NULL UNIQUE)')
        self.db.execute('CREATE UNIQUE INDEX dsg_cache_identity ON features(dsg_id)')
        self.db.execute('CREATE TABLE cache_values(fid INTEGER PRIMARY KEY,feature TEXT NOT NULL,minx REAL,miny REAL,maxx REAL,maxy REAL)')
        if not self.has_geometry:self.db.execute('CREATE VIRTUAL TABLE '+quote(self.rtree)+' USING rtree(id,minx,maxx,miny,maxy)')
        self.names=['fid','dsg_id']+[s['name'] for s in specs]+([self.geometry_column] if self.has_geometry else [])
        self.insert='INSERT OR REPLACE INTO features ('+','.join(map(quote,self.names))+') VALUES ('+','.join('?' for _ in self.names)+')'
        self.uri=self.path+'|layername=features'

    def _value(self,spec,value):
        if value is None:return None
        kind=spec['kind']
        if kind=='integer':return int(value)
        if kind=='real':
            number=values.to_qgis(spec,value)
            if number==0 and math.copysign(1,number)<0:self.signed_zero_fields.add(spec['name'])
            return number
        if kind=='boolean':return int(bool(value))
        if kind=='bytes':return bytes.fromhex(str(value))
        if kind=='json':return values.dumps(value)
        return str(value)

    def _store_page(self,items,z):
        # The caller owns the transaction and cache lock, just as for _store.
        # Keep only one bounded page; duplicate identities retain their last state.
        if len(items)>PAGE_LIMIT:raise ValueError('Página de cache excede o limite de feições.')
        by_id={str(item['feature']['id']):item for item in items}
        if not by_id:return
        known=dict(self.db.execute('SELECT dsg_id,fid FROM ids WHERE dsg_id IN (SELECT value FROM json_each(?))',
                                  (json.dumps(list(by_id)),)))
        new=[];next_fid=None
        for identity in by_id:
            if identity not in known:
                if next_fid is None:next_fid=self.db.execute('SELECT coalesce(max(fid),0)+1 FROM ids').fetchone()[0]
                known[identity]=next_fid;new.append((identity,next_fid));next_fid+=1
        self.db.executemany('INSERT INTO ids VALUES (?,?)',new)
        rows=[];metadata=[];extents=[];ids=[]
        prefix=b'GP\x00\x01'+struct.pack('<i',self.srid)
        for identity,item in by_id.items():
            feature=item['feature'];props=feature['properties'];fid=known[identity]
            if '_bounds' in item:wkb,box=item['_wkb'],item['_bounds']
            else:
                geometry=feature.get('geometry')
                wkb=values.geojson_to_wkb(geometry,z) if geometry else None
                box=values.bounds(geometry) if geometry else None
            row=[fid,identity]+[self._value(s,props.get(s['name'])) for s in self.specs]
            if self.has_geometry:row.append(None if wkb is None else prefix+wkb)
            rows.append(row);ids.append((fid,))
            metadata.append((fid,values.dumps(dict(feature,geometry=None)),*(box or (None,None,None,None))))
            if box:extents.append((fid,box[0],box[2],box[1],box[3]))
        self.db.executemany('DELETE FROM '+quote(self.rtree)+' WHERE id=?',ids)
        self.db.executemany(self.insert,rows)
        self.db.executemany('INSERT OR REPLACE INTO cache_values VALUES (?,?,?,?,?,?)',metadata)
        self.db.executemany('INSERT INTO '+quote(self.rtree)+' VALUES (?,?,?,?,?)',extents)

    def _store(self,dsg_id,text,wkb,box):
        fid=self._fid(dsg_id);feature=values.loads(text)
        props=feature['properties'];feature=dict(feature,geometry=None)
        row=[fid,dsg_id]+[self._value(s,props.get(s['name'])) for s in self.specs]
        if self.has_geometry:row.append(None if wkb is None else b'GP\x00\x01'+struct.pack('<i',self.srid)+wkb)
        self.db.execute('DELETE FROM '+quote(self.rtree)+' WHERE id=?',(fid,))
        self.db.execute(self.insert,row)
        self.db.execute('INSERT OR REPLACE INTO cache_values VALUES (?,?,?,?,?,?)',
            (fid,values.dumps(feature),*(box or (None,None,None,None))))
        if box:self.db.execute('INSERT INTO '+quote(self.rtree)+' VALUES (?,?,?,?,?)',(fid,box[0],box[2],box[1],box[3]))
        return fid

    def clear(self):
        self.db.execute('DELETE FROM features');self.db.execute('DELETE FROM cache_values');self.db.execute('DELETE FROM '+quote(self.rtree))

    def remove(self,dsg_id):
        with self.lock:
            row=self.db.execute('SELECT fid FROM ids WHERE dsg_id=?',(dsg_id,)).fetchone()
            if row:
                self.db.execute('BEGIN IMMEDIATE')
                try:
                    for table,column in [('features','fid'),('cache_values','fid'),(self.rtree,'id')]:
                        self.db.execute('DELETE FROM '+quote(table)+' WHERE '+column+'=?',row)
                    self.db.execute('COMMIT')
                except BaseException:self.db.execute('ROLLBACK');raise

    def _row(self,column,key,result):
        geometry='f.'+quote(self.geometry_column) if self.has_geometry else 'NULL'
        row=self.db.execute('SELECT f.'+result+',c.feature,'+geometry+' FROM features f JOIN cache_values c ON c.fid=f.fid WHERE f.'+column+'=?',(key,)).fetchone()
        if row is None:return None
        feature=values.loads(row[1])
        if row[2] is not None:feature['geometry']=values.wkb_to_geojson(row[2][8:])[0]
        return row[0],values.dumps(feature)

    def by_fid(self,fid):
        with self.lock:return self._row('fid',int(fid),'dsg_id')

    def by_id(self,dsg_id):
        with self.lock:return self._row('dsg_id',dsg_id,'fid')

    def extent(self):
        with self.lock:return self.db.execute('SELECT min(minx),min(miny),max(maxx),max(maxy) FROM cache_values WHERE minx IS NOT NULL').fetchone()

    def get_features(self,request):
        options=QgsDataProvider.ProviderOptions()
        provider=QgsProviderRegistry.instance().createProvider('ogr',self.uri,options,Qgis.DataProviderReadFlag.ForceReadOnly)
        if provider is None or not provider.isValid():raise ValueError('Provedor nativo não abriu o cache GeoPackage.')
        if self.signed_zero_fields:
            # SQLite's numeric column storage drops the sign of zero. A
            # native SQL expression reads just those exceptional attributes
            # from the exact JSON kept for authoritative save planning.
            columns=[]
            for name in self.names:
                column='f.'+quote(name)
                if name in self.signed_zero_fields:
                    path='$.properties.'+name
                    column="CASE WHEN "+column+"=0 THEN CAST(json_extract(c.feature,'"+path+"') AS REAL) ELSE "+column+' END AS '+quote(name)
                columns.append(column)
            sql='SELECT '+','.join(columns)+' FROM features f JOIN cache_values c ON c.fid=f.fid'
            if not provider.setSubsetString(sql):raise ValueError('Leitura exata de zero negativo recusada pelo cache.')
        # OGR's provider iterator owns its feature source, independently of
        # this short-lived provider and its QObject thread affinity.
        return provider.getFeatures(request)
