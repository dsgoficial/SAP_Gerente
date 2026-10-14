"""Vector data provider `dsgversioning`: one dataset of a repository served by DSG Versioning.

SAP 3.0 (contrato-sap.md, seção 7): portado de
`versionamento/qgis_plugin/dsg_versioning_qgis/provider.py` com o cache local e
o canal DSGP/1 intactos. O que mudou: o cliente fala com o repasse do SAP
(`<servidor SAP>/api/versionamento/servico`) com o token do SAP e sem `actor`
(o SAP põe o `X-Dsg-Actor`); o endereço da camada passa a ser lido pelo
`QgsDataSourceUri` do QGIS, com `schema` e `table` da camada do pacote, para
que `dataProvider().uri().schema()/table()` casem a camada como numa do
PostGIS (o formato antigo de `make_uri` continua aceito na leitura); as
mensagens falam do SAP, não do painel antigo.

D024: at headquarters QGIS never writes to the database. A layer of this
provider reads and edits a server-side activity clone through the service
API, never the storage.

Reading. A local SQLite cache with an R*Tree answers every feature request
(extent, fid list and attribute subset pushed down to SQL). Opening reads
only the extent and the count of the class; an iterator with a filter
rectangle loads that region (GET /features with `bbox`, without the map
preview), a request without rectangle loads the whole class once, and fid
requests use what is cached (read back by identity when a reload dropped
them). Loaded regions belong to one generation; a page read at another
generation that this session's own saves do not explain (the RepositoryState
chain) invalidates the cache, keeping the dsg_id -> fid table so fids stay
stable. Loading is serialized by a lock because iterators run on render
threads. The cache is a read copy at one generation: edits go to the service
when the edit buffer is saved and never stay only here.

Layer filter (setSubsetString, SAP Operador 4.1.0). The SAP Operador filters
the review layers by subphase with a QGIS expression. The service filters by
rectangle and identity only, so the reading is the same with or without a
filter (regions, DSGP/1 pages, the cache) and the expression is evaluated
over what the cache returns (SubsetIterator); the count of what passes it is
kept per generation. The filter goes in the `sql` key of the address, as
PostGIS keeps it, so a saved project reopens the layer filtered.

Saving (D026: a save is one service write). The beforeCommitChanges hook
plans the whole edit buffer (changed attributes and geometries, added and
deleted features), validates it locally (identity, types, geometry type, Z,
GEOS validity) and sends ONE POST /features with the generation this layer
saw: the service writes all of it in one transaction or nothing. The
provider write methods QGIS calls next only confirm (and give added features
their fids). Without the hook, each write call is its own batch.

The batch carries a request_id that is stable for the same content: saving
again after a lost response (the edit buffer and the generation seen
unchanged) repeats the key, and the service answers the original result
instead of writing twice. The key is forgotten once a response arrives.

The service must declare the capabilities of compat.REQUIRED_CAPABILITIES;
a layer of a service that lacks one does not open, and says which.

Undo (D026, `undo_last_save`): POST /undo undoes the last save of a live
clone; the cache is read again afterwards.

Repository model (`repository_model`, model.py). When the repository carries
a model, the fields of the layer take from it the labels of the codes the
class accepts (ValueMap editor widget), the default values of a new feature,
the maximum length and the integer ranges; a real of 4 bytes in the source
base is shown and saved as such. The validation of the edit buffer applies
the rules of the model with the codes of the service, and a refusal of the
service (`violations`) is kept per feature and field in `last_violations`.
Without the capability or without a model nothing changes.
"""
import atexit
from dataclasses import dataclass,field
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
from urllib.parse import parse_qsl
from uuid import uuid4
import weakref

from qgis.PyQt.QtCore import QObject,pyqtSignal
from qgis.core import (Qgis,QgsAbstractFeatureIterator,QgsAbstractFeatureSource,QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,QgsCsException,QgsDataProvider,QgsDataSourceUri,QgsEditorWidgetSetup,QgsError,QgsExpression,
    QgsExpressionContext,QgsExpressionContextUtils,QgsFeatureIterator,QgsFeatureRequest,
    QgsField,QgsFieldConstraints,QgsFields,QgsGeometry,QgsMessageLog,QgsProviderMetadata,QgsProviderRegistry,
    QgsRectangle,QgsVectorDataProvider)
from qgis.PyQt.QtCore import QMetaType

from .client import Client,ServiceError,check_url,query
from . import compat
from . import model as model_rules
from . import values

PROVIDER_KEY='dsgversioning'
PAGE_LIMIT=500
ID_FIELD='dsg_id'
CACHE_DIRECTORY=Path(tempfile.gettempdir())/'sap_versionamento_qgis'
LOAD_ATTEMPTS=3
# Identities per GET /features?ids=... when refreshing after a save (the
# service accepts up to 1000; the URL stays short with fewer).
REFRESH_CHUNK=200
# Value QGIS keeps in a ValueMap for "no value" (QgsValueMapFieldFormatter::NULL_VALUE).
VALUE_MAP_NULL='{2839923C-8B7D-419E-B84B-CA2FE9B80EC7}'
INT32_MIN=-(2**31); INT32_MAX=2**31-1


# Connections -------------------------------------------------------------------
# The token lives only here, in memory, registered by the plugin when it
# connects. The layer URI (saved in projects) carries service, repository and
# dataset, never the token. SAP 3.0: the token is the SAP's own (a function,
# read at each request) and there is no actor: the SAP sets X-Dsg-Actor.

LOG_TAG='SAP Versionamento'
NOT_CONNECTED=' Entre no plugin do SAP com seu usuário: o token não é gravado no projeto.'


class Connection:
    def __init__(self,url,token,actor=None,reauth=None):
        self.client=Client(url,token,reauth)
        self._actor=actor
        self._capabilities=None
        self._lock=threading.Lock()
        # Models of the repositories of this service, one download per digest.
        self.models=model_rules.Models()

    def actor(self):
        """'' in the SAP: the identity of a write is the login of the token (X-Dsg-Actor)."""
        value=self._actor() if callable(self._actor) else self._actor
        return (value or '').strip()

    def capabilities(self):
        """Capabilities the service declares in /api/info. A service that
        lacks one this plugin needs is refused (compat.refusal)."""
        with self._lock:
            if self._capabilities is None:
                info=self.client.request('/info')
                refused=compat.refusal(info)
                if refused: raise ValueError(refused)
                self._capabilities=frozenset(info.get('capabilities') or [])
                self._limits=dict(info.get('limits') or {})
            return self._capabilities

    def limits(self):
        """Limits the service announces in /api/info (D044), {} when it announces none."""
        self.capabilities()
        return getattr(self,'_limits',{})

    def repository_model(self,repo):
        """(model document or None, required fields per class) of `repo`;
        (None, {}) when the service does not declare the model."""
        if model_rules.CAPABILITY not in self.capabilities(): return None,{}
        return self.models.repository(self.client,repo)

    def rules(self,repo,spec):
        """Rules of the class `spec` in `repo`, or None without model."""
        document,required=self.repository_model(repo)
        if document is None: return None
        return model_rules.class_rules(document,required,spec)


_connections={}
_connections_lock=threading.Lock()


def register_connection(url,token,actor=None,reauth=None):
    connection=Connection(url,token,actor,reauth)
    with _connections_lock:
        previous=_connections.get(connection.client.url)
        # The models are immutable and identified by digest: connecting again keeps them.
        if previous is not None: connection.models=previous.models
        _connections[connection.client.url]=connection
    return connection


def widget_setup(spec,rules):
    """Editor widget the model asks for a field: the labels of the codes the
    class accepts, or the range of an integer; None when it asks nothing."""
    if rules is None: return None
    rule=rules.rule(spec['name'])
    if rule.get('list'): return None
    codes=rules.codes(spec['name'])
    if codes is not None:
        entries=[{label:str(code)} for code,label in codes]
        if spec.get('nullable') is not False: entries.insert(0,{'(sem valor)':VALUE_MAP_NULL})
        return QgsEditorWidgetSetup('ValueMap',{'map':entries})
    if spec['kind']=='integer' and ('min' in rule or 'max' in rule):
        low=rule.get('min',INT32_MIN); high=rule.get('max',INT32_MAX)
        if INT32_MIN<=low<=high<=INT32_MAX:
            return QgsEditorWidgetSetup('Range',{'Min':int(low),'Max':int(high),'Step':1,'Style':'SpinBox','AllowNull':spec.get('nullable') is not False})
    return None


def connection_for(url):
    with _connections_lock: return _connections.get(check_url(url))


def make_uri(service,repo,dataset,schema='',table=None,subset=''):
    """Address of a layer in the key='value' form QgsDataSourceUri reads:
    `service`, `repo` and `dataset` for the provider, `schema` and `table`
    (the layer of the SAP package) for whoever matches layers by
    `dataProvider().uri().schema()/table()`, and the layer filter
    (setSubsetString) in `sql`, as PostGIS keeps it, so a saved project
    reopens the layer filtered."""
    uri=QgsDataSourceUri()
    uri.setDataSource(str(schema or ''),str(table or dataset),'',str(subset or ''))
    uri.setParam('service',check_url(service))
    uri.setParam('repo',str(repo))
    uri.setParam('dataset',str(dataset))
    return uri.uri(False).strip()


def parse_uri(uri):
    """Parts of a layer address: the QgsDataSourceUri form of make_uri, or the
    former urlencoded form (service=...&repo=...&dataset=..., never with spaces)."""
    text=str(uri or '').strip()
    if ' ' in text:
        source=QgsDataSourceUri(text)
        parts={'service':source.service() or source.param('service'),'repo':source.param('repo'),
               'dataset':source.param('dataset'),'schema':source.schema(),'table':source.table(),
               'subset':source.sql()}
    else:
        parts=dict(parse_qsl(text,keep_blank_values=True))
    missing=[key for key in ('service','repo','dataset') if not parts.get(key)]
    if missing:
        raise ValueError('Endereço de camada do versionamento incompleto: falta '+', '.join(missing)+'.')
    parts['service']=check_url(parts['service'])
    parts.setdefault('schema','')
    parts['subset']=str(parts.get('subset') or '').strip()
    if not parts.get('table'): parts['table']=parts['dataset']
    return parts


class RepositoryState:
    """Generations this QGIS session produced in one repository.

    The API generation is repository-wide: saving one layer changes the
    generation every other layer of the same activity saw. Each successful
    write records `before -> (after, dataset, writer)`; a layer can follow
    the chain from the generation its cache was read at while the steps were
    writes by other layers to other datasets, which cannot have changed its
    features. A foreign write leaves no step, so the service still refuses
    the layer as stale."""
    LIMIT=100000

    def __init__(self):
        self.lock=threading.Lock()
        self.transitions={}

    def record(self,before,after,dataset,writer):
        with self.lock:
            if len(self.transitions)>=self.LIMIT: self.transitions.clear()
            self.transitions[before]=(after,dataset,writer)

    def follow(self,generation,dataset,writer):
        with self.lock:
            seen=set()
            while generation in self.transitions and generation not in seen:
                seen.add(generation)
                after,step_dataset,step_writer=self.transitions[generation]
                if step_dataset==dataset and step_writer!=writer: break
                generation=after
            return generation


_repositories={}


def repository_state(service,repo):
    with _connections_lock:
        return _repositories.setdefault((service,repo),RepositoryState())


class ProviderEvents(QObject):
    """Save outcomes for the plugin: (layer source, kind, message).

    kind is 'stale' (the activity changed in the service; reload), 'refused'
    (the service refused the save), 'local' (refused before any write) or
    'saved'."""
    saveReport=pyqtSignal(str,str,str)


events=ProviderEvents()


# Local read cache --------------------------------------------------------------

def _cleanup_old_caches():
    try:
        CACHE_DIRECTORY.mkdir(parents=True,exist_ok=True)
        limit=time.time()-86400
        for path in list(CACHE_DIRECTORY.glob('*.sqlite*'))+list(CACHE_DIRECTORY.glob('*.gpkg*')):
            try:
                if path.stat().st_mtime<limit: path.unlink()
            except OSError:
                pass
    except OSError:
        pass


_cleanup_old_caches()


class Cache:
    SCHEMA='''
    CREATE TABLE ids(dsg_id TEXT PRIMARY KEY, fid INTEGER NOT NULL UNIQUE);
    CREATE TABLE features(fid INTEGER PRIMARY KEY, dsg_id TEXT NOT NULL UNIQUE, feature TEXT NOT NULL, wkb BLOB,
                          minx REAL, miny REAL, maxx REAL, maxy REAL);
    CREATE VIRTUAL TABLE extent_index USING rtree(fid, minx, maxx, miny, maxy);
    '''

    def __init__(self):
        CACHE_DIRECTORY.mkdir(parents=True,exist_ok=True)
        self.path=str(CACHE_DIRECTORY/(uuid4().hex+'.sqlite'))
        self.db=sqlite3.connect(self.path,check_same_thread=False,isolation_level=None)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=OFF')
        self.db.executescript(self.SCHEMA)
        self.lock=threading.RLock()

    def reader(self):
        db=sqlite3.connect(Path(self.path).as_uri()+'?mode=ro',uri=True,check_same_thread=False)
        return db

    def _fid(self,dsg_id):
        row=self.db.execute('SELECT fid FROM ids WHERE dsg_id=?',(dsg_id,)).fetchone()
        if row: return row[0]
        fid=self.db.execute('SELECT coalesce(max(fid),0)+1 FROM ids').fetchone()[0]
        self.db.execute('INSERT INTO ids VALUES (?,?)',(dsg_id,fid))
        return fid

    def _store(self,dsg_id,text,wkb,box):
        fid=self._fid(dsg_id)
        self.db.execute('DELETE FROM extent_index WHERE fid=?',(fid,))
        self.db.execute('INSERT OR REPLACE INTO features VALUES (?,?,?,?,?,?,?,?)',
                        (fid,dsg_id,text,wkb,*(box if box else (None,None,None,None))))
        if box: self.db.execute('INSERT INTO extent_index VALUES (?,?,?,?,?)',(fid,box[0],box[2],box[1],box[3]))
        return fid

    def _store_page(self,items,z):
        if len(items)>PAGE_LIMIT:raise ValueError('Página de cache excede o limite de feições.')
        for item in items:self._store(*page_row(item,z))

    def begin(self):
        self.lock.acquire(); self.db.execute('BEGIN IMMEDIATE')

    def commit(self):
        try: self.db.execute('COMMIT')
        finally: self.lock.release()

    def rollback(self):
        try: self.db.execute('ROLLBACK')
        finally: self.lock.release()

    def clear(self):
        self.db.execute('DELETE FROM features'); self.db.execute('DELETE FROM extent_index')

    def put(self,dsg_id,text,wkb,box):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                fid=self._store(dsg_id,text,wkb,box)
                self.db.execute('COMMIT')
            except BaseException:
                self.db.execute('ROLLBACK'); raise
            return fid

    def remove(self,dsg_id):
        with self.lock:
            row=self.db.execute('SELECT fid FROM features WHERE dsg_id=?',(dsg_id,)).fetchone()
            if row:
                self.db.execute('BEGIN IMMEDIATE')
                self.db.execute('DELETE FROM features WHERE fid=?',(row[0],))
                self.db.execute('DELETE FROM extent_index WHERE fid=?',(row[0],))
                self.db.execute('COMMIT')

    def by_fid(self,fid):
        with self.lock:
            return self.db.execute('SELECT dsg_id,feature FROM features WHERE fid=?',(int(fid),)).fetchone()

    def by_id(self,dsg_id):
        with self.lock:
            return self.db.execute('SELECT fid,feature FROM features WHERE dsg_id=?',(dsg_id,)).fetchone()

    def count(self):
        with self.lock: return self.db.execute('SELECT count(*) FROM features').fetchone()[0]

    def extent(self):
        with self.lock:
            return self.db.execute('SELECT min(minx),min(miny),max(maxx),max(maxy) FROM features WHERE minx IS NOT NULL').fetchone()

    def close(self):
        try: self.db.close()
        except sqlite3.Error: pass
        for suffix in ('','-wal','-shm'):
            try: os.remove(self.path+suffix)
            except OSError: pass


_open_caches=weakref.WeakSet()


@atexit.register
def _close_caches():
    for cache in list(_open_caches): cache.close()


def cache_row(feature,z):
    """(dsg_id, feature text, WKB, bounds) of a feature read with `values.loads`."""
    geometry=feature.get('geometry')
    wkb=box=None
    if geometry:
        wkb=values.geojson_to_wkb(geometry,z)
        box=values.bounds(geometry)
    return str(feature['id']),values.dumps(feature),wkb,box


def page_row(item,z):
    if '_bounds' in item:
        feature=item['feature']
        return str(feature['id']),values.dumps(feature),item['_wkb'],item['_bounds']
    return cache_row(item['feature'],z)


def _contains(outer,inner):
    return outer[0]<=inner[0] and outer[1]<=inner[1] and outer[2]>=inner[2] and outer[3]>=inner[3]


class ReadCancelled(Exception):
    pass


def check_cancelled(feedback):
    if feedback is not None and feedback.isCanceled():raise ReadCancelled()


class Loader:
    """Fills the cache of one layer from the service: regions, or the whole class.

    Thread-safe: render threads and the main thread ask for regions through
    `ensure`, serialized by one lock. `generation` is the generation every
    cached feature belongs to. `resets` counts the times the cache was
    (re)initialized from the service (opening, reload, invalidation)."""

    def __init__(self,parts,cache,z,writer):
        self.parts=parts; self.cache=cache; self.z=z; self.writer=writer
        self.lock=threading.RLock()
        self.generation=None; self.regions=[]; self.full=False
        self.resets=0; self.full_reads=0; self.region_reads=0; self.pages=0

    def _client(self):
        connection=connection_for(self.parts['service'])
        if connection is None:
            raise ValueError('Sem conexão com o versionamento do SAP ('+self.parts['service']+') para ler esta camada.'+NOT_CONNECTED)
        return connection.client

    def reset(self,generation):
        """Forget every cached feature and region (the fid table stays)."""
        with self.lock:
            self.cache.begin()
            try: self.cache.clear()
            except BaseException: self.cache.rollback(); raise
            self.cache.commit()
            self.regions=[]; self.full=False; self.generation=generation; self.resets+=1

    def follow(self):
        """The generation past this session's own saves (RepositoryState chain)."""
        with self.lock:
            if self.generation is not None:
                self.generation=repository_state(self.parts['service'],self.parts['repo']).follow(
                    self.generation,self.parts['dataset'],self.writer)
            return self.generation

    def _consistent(self,page_generation):
        if self.generation is None:
            self.generation=page_generation; return True
        if page_generation==self.generation: return True
        if self.follow()==page_generation: return True
        return False

    def ensure(self,rect=None,feedback=None):
        """Make the cache hold every feature whose envelope meets `rect`
        (minx, miny, maxx, maxy in the layer CRS), or the whole class."""
        with self.lock:
            check_cancelled(feedback)
            if self.full: return
            if rect is not None and any(_contains(region,rect) for region in self.regions):
                return
            self._load(rect,feedback)

    def ensure_fids(self,fids,feedback=None):
        """Read back features known by fid that are not cached (after a reload
        or an invalidation, the dsg_id -> fid table outlives the features)."""
        with self.lock:
            check_cancelled(feedback)
            if self.full: return
            for _ in range(LOAD_ATTEMPTS):
                with self.cache.lock:
                    missing=[row[0] for row in self.cache.db.execute(
                        'SELECT i.dsg_id FROM ids i WHERE i.fid IN (SELECT value FROM json_each(?)) '
                        'AND NOT EXISTS (SELECT 1 FROM features f WHERE f.fid=i.fid)',(json.dumps([int(f) for f in fids]),))]
                if not missing: return
                client=self._client(); reset=False
                for start in range(0,len(missing),REFRESH_CHUNK):
                    check_cancelled(feedback)
                    chunk=missing[start:start+REFRESH_CHUNK]
                    after=''
                    self.cache.begin()
                    try:
                        while True:
                            check_cancelled(feedback)
                            page=client.feature_page('/repos/'+self.parts['repo']+'/features'+query(
                                dataset=self.parts['dataset'],ids=json.dumps(chunk),after=after,limit=500,map_geometry='false'),
                                materialize_geometry=not getattr(self.cache,'native',False))
                            check_cancelled(feedback)
                            generation=int(page['generation'])
                            if not self._consistent(generation):reset=True;break
                            self.cache._store_page(page['items'],self.z)
                            self.pages+=1
                            if page.get('next') is None:break
                            following=str(page['next'])
                            if following<=after:raise ServiceError('Paginação sem avanço; leitura interrompida.')
                            after=following
                    except BaseException:
                        self.cache.rollback(); raise
                    if reset:
                        self.cache.rollback();self.reset(generation);break
                    self.cache.commit()
                if not reset: return
            raise ServiceError('A atividade mudou durante a releitura por identidade; tente de novo.',409)

    def _load(self,rect,feedback=None):
        client=self._client()
        for _ in range(LOAD_ATTEMPTS):
            after=''; first=None; restart=False; foreign=False
            self.cache.begin()
            try:
                while True:
                    check_cancelled(feedback)
                    parameters=dict(dataset=self.parts['dataset'],after=after,limit=PAGE_LIMIT,map_geometry='false')
                    if rect is not None: parameters['bbox']=','.join(repr(float(v)) for v in rect)
                    page=client.feature_page('/repos/'+self.parts['repo']+'/features'+query(**parameters),
                        materialize_geometry=not getattr(self.cache,'native',False))
                    check_cancelled(feedback)
                    generation=int(page['generation'])
                    if first is None:
                        first=generation
                        if not self._consistent(generation):
                            foreign=True; break
                    elif generation!=first:
                        restart=True; break
                    self.cache._store_page(page['items'],self.z)
                    self.pages+=1
                    if page.get('next') is None: break
                    following=str(page['next'])
                    if following<=after:raise ServiceError('Paginação sem avanço; leitura interrompida.')
                    after=following
                if restart or foreign:
                    self.cache.rollback()
                    # Another writer changed the activity: what is cached may
                    # be stale, so everything is read again at the new generation.
                    if foreign: self.reset(first)
                    continue
                self.cache.commit()
            except BaseException:
                self.cache.rollback(); raise
            self.generation=first
            if rect is None: self.full=True; self.full_reads+=1
            else: self.regions.append(tuple(rect)); self.region_reads+=1
            return
        raise ServiceError('A atividade mudou durante a leitura em '+str(LOAD_ATTEMPTS)+' tentativas; tente de novo.',409)


# Reading -------------------------------------------------------------------------

class FeatureSource(QgsAbstractFeatureSource):
    """Snapshot of what an iterator needs; independent of the provider's lifetime."""
    def __init__(self,provider):
        super().__init__()
        self.cache_path=provider._cache.path if provider._cache else None
        self.loader=provider._loader
        self.fields=QgsFields(provider._fields)
        self.specs=list(provider._specs)
        self.crs=QgsCoordinateReferenceSystem(provider._crs)
        self.native_cache=provider._cache if getattr(provider._cache,'native',False) else None
        self.subset=provider._subset

    def getFeatures(self,request=QgsFeatureRequest()):
        if self.subset:
            return QgsFeatureIterator(SubsetIterator(self,request))
        return self.read(request)

    def read(self,request):
        """Iterator over the cache, loading from the service what `request` needs."""
        if self.native_cache:
            preparation=FeatureIterator(self,request,prepare_only=True)
            if preparation._closed:return QgsFeatureIterator()
            return self.native_cache.get_features(request)
        return QgsFeatureIterator(FeatureIterator(self,request))


def subset_expression(text,fields):
    """(QgsExpression, referenced field indexes or None for all) of a layer
    filter; ValueError when it does not parse or names a missing field."""
    expression=QgsExpression(text)
    if expression.hasParserError():
        raise ValueError('Filtro da camada inválido ('+expression.parserErrorString()+'): '+text)
    indexes=set()
    for name in expression.referencedColumns():
        if name==QgsFeatureRequest.ALL_ATTRIBUTES: return expression,None
        index=fields.lookupField(name)
        if index<0: raise ValueError('Filtro da camada cita o campo '+name+', que a classe não tem: '+text)
        indexes.add(index)
    return expression,indexes


def _truthy(value):
    """Value of a filter as QGIS reads a condition: NULL and zero are false."""
    if value is None: return False
    if isinstance(value,(bool,int,float)): return bool(value)
    try: return float(str(value))!=0
    except ValueError: return False


class SubsetIterator(QgsAbstractFeatureIterator):
    """The layer filter (setSubsetString), evaluated here on what the cache
    returns: the service filters only by rectangle and identity, so the
    reading (regions, DSGP/1 pages, local cache) is the same with or without
    the filter, and the filter only drops features from the answer."""

    def __init__(self,source,request):
        super().__init__(request)
        self._expression,indexes=subset_expression(source.subset,source.fields)
        self._context=QgsExpressionContext()
        self._context.appendScope(QgsExpressionContextUtils.globalScope())
        self._context.setFields(source.fields)
        self._expression.prepare(self._context)
        inner=QgsFeatureRequest(request)
        # The limit counts what passes the filter: it is applied here.
        inner.setLimit(-1)
        flags=inner.flags()
        if flags&Qgis.FeatureRequestFlag.SubsetOfAttributes:
            if indexes is None:
                inner.setFlags(flags&~Qgis.FeatureRequestFlag.SubsetOfAttributes)
            else:
                inner.setSubsetOfAttributes(sorted(set(request.subsetOfAttributes())|indexes))
        if self._expression.needsGeometry() and inner.flags()&Qgis.FeatureRequestFlag.NoGeometry:
            inner.setFlags(inner.flags()&~Qgis.FeatureRequestFlag.NoGeometry)
        self._inner=source.read(inner)

    def fetchFeature(self,feature):
        while self._inner.nextFeature(feature):
            self._context.setFeature(feature)
            if _truthy(self._expression.evaluate(self._context)):
                return True
        feature.setValid(False)
        return False

    def rewind(self):
        return self._inner.rewind()

    def close(self):
        return self._inner.close()


class FeatureIterator(QgsAbstractFeatureIterator):
    def __init__(self,source,request,prepare_only=False):
        super().__init__(request)
        self._source=source
        self._request=QgsFeatureRequest(request)
        self._db=None; self._cursor=None; self._closed=False
        self._transform=QgsCoordinateTransform()
        destination=request.destinationCrs()
        if destination.isValid() and source.crs.isValid() and destination!=source.crs:
            self._transform=QgsCoordinateTransform(source.crs,destination,request.transformContext())
        try:
            self._rect=self.filterRectToSourceCrs(self._transform)
        except QgsCsException:
            self._closed=True; return
        self._distance=None
        if request.spatialFilterType()==Qgis.SpatialFilterType.DistanceWithin:
            reference=QgsGeometry(request.referenceGeometry())
            if self._transform.isValid():
                reference.transform(self._transform,Qgis.TransformDirection.Reverse)
            self._distance=(reference,request.distanceWithin())
        flags=request.flags()
        self._exact=bool(flags&Qgis.FeatureRequestFlag.ExactIntersect) and not self._rect.isNull()
        self._want_geometry=not bool(flags&Qgis.FeatureRequestFlag.NoGeometry)
        self._need_geometry=self._want_geometry or self._exact or self._distance is not None
        count=len(source.fields)
        if flags&Qgis.FeatureRequestFlag.SubsetOfAttributes:
            self._attributes=sorted(i for i in request.subsetOfAttributes() if 0<=i<count)
        else:
            self._attributes=list(range(count))
        self._need_text=any(i>0 for i in self._attributes)
        self._fill()
        if not prepare_only:self._start()

    def _fill(self):
        """Load what this request needs into the cache (fid requests read back only uncached identities)."""
        loader=self._source.loader
        if self._closed or loader is None: return
        kind=self._request.filterType()
        feedback=self._request.feedback()
        try:
            if kind==Qgis.FeatureRequestFilterType.Fid:
                loader.ensure_fids([self._request.filterFid()],feedback); return
            if kind==Qgis.FeatureRequestFilterType.Fids:
                loader.ensure_fids(list(self._request.filterFids()),feedback); return
        except ReadCancelled:
            self._closed=True;return
        except (ServiceError,ValueError,sqlite3.Error) as error:
            self._closed=True
            QgsMessageLog.logMessage('Leitura pelo serviço falhou: '+str(error),LOG_TAG,Qgis.MessageLevel.Warning)
            return
        rect=None if self._rect.isNull() else (self._rect.xMinimum(),self._rect.yMinimum(),self._rect.xMaximum(),self._rect.yMaximum())
        try:
            loader.ensure(rect,feedback)
        except ReadCancelled:
            self._closed=True;return
        except (ServiceError,ValueError,sqlite3.Error) as error:
            self._closed=True
            QgsMessageLog.logMessage('Leitura pelo serviço falhou: '+str(error),LOG_TAG,Qgis.MessageLevel.Warning)

    def _start(self):
        if self._closed or not self._source.cache_path: self._closed=True; return
        try:
            if self._db is None: self._db=sqlite3.connect(Path(self._source.cache_path).as_uri()+'?mode=ro',uri=True,check_same_thread=False)
        except sqlite3.Error:
            self._closed=True; return
        columns='f.fid,f.dsg_id,'+('f.feature' if self._need_text else 'NULL')+','+('f.wkb' if self._need_geometry else 'NULL')
        sql='SELECT '+columns+' FROM features f'
        where=[]; parameters=[]
        if not self._rect.isNull():
            sql+=' JOIN extent_index r ON r.fid=f.fid'
            # The R*Tree keeps float32 bounds rounded outwards; the REAL
            # columns make the bounding-box test exact.
            box=[self._rect.xMaximum(),self._rect.xMinimum(),self._rect.yMaximum(),self._rect.yMinimum()]
            where.append('r.minx<=? AND r.maxx>=? AND r.miny<=? AND r.maxy>=?')
            where.append('f.minx<=? AND f.maxx>=? AND f.miny<=? AND f.maxy>=?')
            parameters+=box+box
        kind=self._request.filterType()
        if kind==Qgis.FeatureRequestFilterType.Fid:
            where.append('f.fid=?'); parameters.append(int(self._request.filterFid()))
        elif kind==Qgis.FeatureRequestFilterType.Fids:
            where.append('f.fid IN (SELECT value FROM json_each(?))')
            parameters.append('['+','.join(str(int(f)) for f in self._request.filterFids())+']')
        if where: sql+=' WHERE '+' AND '.join(where)
        sql+=' ORDER BY f.fid'
        try:
            self._cursor=self._db.execute(sql,parameters)
        except sqlite3.Error:
            self._closed=True

    def fetchFeature(self,feature):
        if self._request.feedback() is not None and self._request.feedback().isCanceled():self.close()
        if self._closed or self._cursor is None:
            feature.setValid(False); return False
        while True:
            try: row=self._cursor.fetchone()
            except sqlite3.Error: row=None
            if row is None:
                self.close(); feature.setValid(False); return False
            fid,dsg_id,text,wkb=row
            geometry=None
            if wkb is not None and self._need_geometry:
                geometry=QgsGeometry(); geometry.fromWkb(wkb)
                if self._exact and not geometry.intersects(self._rect): continue
                if self._distance and geometry.distance(self._distance[0])>self._distance[1]: continue
            elif self._exact or self._distance:
                continue
            feature.setFields(self._source.fields,True)
            feature.setId(fid)
            attributes=[None]*len(self._source.fields)
            if self._attributes and self._attributes[0]==0: attributes[0]=dsg_id
            if self._need_text:
                properties=values.loads(text)['properties']
                for index in self._attributes:
                    if index==0: continue
                    spec=self._source.specs[index-1]
                    attributes[index]=values.to_qgis(spec,properties.get(spec['name']))
            feature.setAttributes(attributes)
            if geometry is not None and self._want_geometry:
                if self._transform.isValid():
                    try: geometry.transform(self._transform)
                    except QgsCsException: continue
                feature.setGeometry(geometry)
            else:
                feature.clearGeometry()
            feature.setValid(True)
            return True

    def rewind(self):
        if self._closed and self._db is None: return False
        self._closed=False
        self._start()
        return not self._closed

    def close(self):
        self._closed=True
        if self._db is not None:
            try: self._db.close()
            except sqlite3.Error: pass
            self._db=None; self._cursor=None
        return True


# Saving --------------------------------------------------------------------------

@dataclass
class Operation:
    verb: str               # 'put' or 'delete'
    dsg_id: str
    feature: dict=None      # desired state for 'put'
    added_fid: int=None     # edit-buffer id of an added feature


@dataclass
class SaveRecord:
    """What one save wrote; `undo_last_save` undoes it while the clone lives (D026)."""
    hooked: bool
    started: float=field(default_factory=time.time)
    actor: str=''
    generation_before: int=None
    generation_after: int=None
    written: list=field(default_factory=list)   # (verb, dsg_id, state before as text or None)
    skipped: list=field(default_factory=list)
    failed: list=field(default_factory=list)    # (dsg_id, message)
    # Batch save: the whole buffer was sent by the hook; the write methods
    # QGIS calls next only confirm. `revision` is the save's revision.
    sent: bool=False
    finished: bool=False
    revision: str=None


class LocalRefusal(ValueError):
    """A save refused by the provider; `announced` when the plugin was already
    told. `violations` lists what the repository model refused."""
    def __init__(self,message,announced=False,violations=None):
        super().__init__(message)
        self.announced=announced
        self.violations=list(violations or [])


# The provider ---------------------------------------------------------------------

class DsgVersioningProvider(QgsVectorDataProvider):

    @classmethod
    def providerKey(cls):
        return PROVIDER_KEY

    @classmethod
    def description(cls):
        return 'Versionamento do SAP: atividade editada pelo serviço'

    @classmethod
    def createProvider(cls,uri,providerOptions,flags=Qgis.DataProviderReadFlags()):
        return DsgVersioningProvider(uri,providerOptions,flags)

    def __init__(self,uri='',providerOptions=QgsDataProvider.ProviderOptions(),flags=Qgis.DataProviderReadFlags()):
        super().__init__(uri,providerOptions,flags)
        self._uri=uri; self._valid=False
        self._fields=QgsFields(); self._specs=[]; self._dataset=None
        self._wkb_type=Qgis.WkbType.NoGeometry; self._geometry_type=None; self._z=False
        self._crs=QgsCoordinateReferenceSystem(); self._extent=QgsRectangle()
        self._cache=None; self._loader=None; self._count=0
        self._id_index=1 if os.environ.get('DSG_QGIS_NATIVE_CACHE','1')=='1' else 0
        self._save_keys={}
        self._refusal=None; self._save=None; self.save_log=[]; self._added_ids={}; self._writer=uuid4().hex
        self.open_stats={}; self._reloading=False
        # Rules of the class in the repository model (None without model), and
        # whether the buffer is checked against them before a save (a test
        # turns it off to see the refusal of the service).
        self.rules=None; self.model_check=True; self._violations=[]
        # Layer filter (setSubsetString), evaluated over the cache; the count
        # of what passes it is kept for the generation it was counted at.
        self._subset=''; self._counted=None
        try:
            self._parts=parse_uri(uri)
            self._open()
            if self._parts['subset']:
                subset_expression(self._parts['subset'],self._fields)
                self._subset=self._parts['subset']
            self._valid=True
            # QgsVectorLayer.reload() reaches QgsDataProvider::reloadData, which
            # does not dispatch reloadProviderData to Python but emits
            # dataChanged: that signal is what brings the service state back.
            self.dataChanged.connect(self._data_changed)
        except (ServiceError,ValueError,KeyError,sqlite3.Error) as error:
            message=str(error) or type(error).__name__
            self.setError(QgsError('Versionamento do SAP: '+message,PROVIDER_KEY))
            self.open_error=message

    # Opening ---------------------------------------------------------------

    def _connection(self):
        connection=connection_for(self._parts['service'])
        if connection is None:
            raise ValueError('Sem conexão com o versionamento do SAP ('+self._parts['service']+') para abrir esta camada.'+NOT_CONNECTED)
        return connection

    def _path(self,suffix):
        return '/repos/'+self._parts['repo']+suffix

    def _open(self):
        started=time.perf_counter()
        connection=self._connection(); client=connection.client
        # Refuses a service without the capabilities this plugin needs.
        connection.capabilities()
        datasets=values.loads(client.request_text(self._path('/datasets')))['datasets']
        spec=next((d for d in datasets if d['name']==self._parts['dataset']),None)
        if spec is None:
            raise ValueError('Classe '+self._parts['dataset']+' ausente no repositório.')
        self._dataset=spec
        self._specs=[dict(f,precision=None if f.get('precision') is None else int(f['precision']),
                          scale=None if f.get('scale') is None else int(f['scale'])) for f in spec['fields']]
        try:
            self.rules=connection.rules(self._parts['repo'],spec)
        except (ServiceError,ValueError,KeyError,TypeError) as error:
            # The service enforces the model anyway; the layer opens without its help.
            self.rules=None
            QgsMessageLog.logMessage('Modelo do repositório não lido: '+str(error),LOG_TAG,Qgis.MessageLevel.Warning)
        rules=self.rules
        fields=QgsFields()
        if self._id_index:
            fields.append(QgsField('fid',QMetaType.Type.LongLong,'integer',0,0,'identificador local do cache'))
        identity=QgsField(ID_FIELD,QMetaType.Type.QString,'text',0,0,'identidade persistente do DSG Versioning')
        constraints=QgsFieldConstraints()
        constraints.setConstraint(QgsFieldConstraints.Constraint.ConstraintNotNull,QgsFieldConstraints.ConstraintOrigin.ConstraintOriginProvider)
        constraints.setConstraint(QgsFieldConstraints.Constraint.ConstraintUnique,QgsFieldConstraints.ConstraintOrigin.ConstraintOriginProvider)
        identity.setConstraints(constraints)
        fields.append(identity)
        for item in self._specs:
            rule=rules.rule(item['name']) if rules else {}
            if rules is not None:
                if rules.single(item['name']): item['single']=True
                # NOT NULL of the class specification, as the model route reports it.
                if item['name'] in rules.required: item['nullable']=False
            kind,type_name,length,precision,comment=values.field_type(item)
            if item['kind']=='text' and rule.get('max_length') is not None: length=int(rule['max_length'])
            if rule.get('domain'): comment=(comment+'; ' if comment else '')+'domínio '+str(rule['domain'])
            qgs_field=QgsField(item['name'],kind,type_name,length,precision,comment)
            if item.get('nullable') is False:
                required=QgsFieldConstraints()
                required.setConstraint(QgsFieldConstraints.Constraint.ConstraintNotNull,QgsFieldConstraints.ConstraintOrigin.ConstraintOriginProvider)
                qgs_field.setConstraints(required)
            setup=widget_setup(item,rules)
            if setup is not None: qgs_field.setEditorWidgetSetup(setup)
            fields.append(qgs_field)
        self._fields=fields
        if spec.get('geometry_type'):
            self._geometry_type=spec['geometry_type']; self._z=bool(spec.get('z'))
            self._wkb_type=Qgis.WkbType(values.wkb_code(self._geometry_type,self._z))
            self._crs=QgsCoordinateReferenceSystem('EPSG:'+str(int(spec['srid'])))
        if self._id_index:
            from .native_cache import NativeCache
            self._cache=NativeCache(self._specs,self._geometry_type,self._z,int(spec.get('srid',4326)))
        else:self._cache=Cache()
        _open_caches.add(self._cache)
        weakref.finalize(self,self._cache.close)
        self._loader=Loader(self._parts,self._cache,self._z,self._writer)
        self._loader.resets=1
        self._fill_initial(client)
        self.open_stats['seconds']=time.perf_counter()-started

    def _fill_initial(self,client=None):
        """Opening or reload: the extent and the count of the class only."""
        client=client or self._connection().client
        extent=values.loads(client.request_text(self._path('/extent')+query(dataset=self._parts['dataset'])))
        self._loader.generation=int(extent['generation'])
        self._count=int(extent['count'])
        box=extent.get('extent')
        self._extent=QgsRectangle() if not box else QgsRectangle(*[float(v) for v in box])
        self.open_stats.update(pages=0,features=self._count,generation=self._loader.generation,mode='extensão')

    def _compute_extent(self):
        box=self._cache.extent() if self._cache else None
        self._extent=QgsRectangle() if not box or box[0] is None else QgsRectangle(box[0],box[1],box[2],box[3])

    # QgsDataProvider / QgsVectorDataProvider --------------------------------

    def name(self): return PROVIDER_KEY
    def isValid(self): return self._valid
    def crs(self): return QgsCoordinateReferenceSystem(self._crs)
    def extent(self): return QgsRectangle(self._extent)
    def updateExtents(self):
        if self._cache and self._loader.full: self._compute_extent()
    def wkbType(self): return self._wkb_type
    def fields(self): return QgsFields(self._fields)
    def featureCount(self):
        if not self._cache: return 0
        if self._subset: return self._subset_count()
        return self._cache.count() if self._loader.full else self._count
    def dataSourceUri(self,expandAuthConfig=False): return self._uri
    def storageType(self): return 'Versionamento do SAP (clone da atividade no servidor)'
    def supportsSubsetString(self): return True
    def subsetString(self): return self._subset

    def setSubsetString(self,subset,updateFeatureCount=True):
        """Filter of the layer, a QGIS expression over its fields (the SAP
        Operador filters the review layers by subphase). The service filters
        by rectangle and identity only: the reading stays the same and the
        expression is evaluated over what the cache returns (SubsetIterator).
        Refused, keeping the current filter, when it does not parse or names
        a missing field."""
        text=str(subset or '').strip()
        if text:
            try: subset_expression(text,self._fields)
            except ValueError as error:
                self.pushError(str(error)); return False
        self._subset=text; self._counted=None
        parts=self._parts
        self._uri=make_uri(parts['service'],parts['repo'],parts['dataset'],parts['schema'],parts['table'],text)
        self._parts=dict(parts,subset=text)
        return True

    def _subset_count(self):
        """Features that pass the filter: the class is read whole (once per
        generation) and the filter counted over the cache."""
        loader=self._loader
        def state(): return (self._subset,loader.generation,loader.resets,loader.full)
        if self._counted is not None and self._counted[0]==state():
            return self._counted[1]
        request=QgsFeatureRequest().setFlags(Qgis.FeatureRequestFlag.NoGeometry).setNoAttributes()
        found=0
        for _ in FeatureSource(self).getFeatures(request): found+=1
        self._counted=(state(),found)
        return found
    def pkAttributeIndexes(self): return [self._id_index]
    def featureSource(self): return FeatureSource(self)

    def getFeatures(self,request=QgsFeatureRequest()):
        return FeatureSource(self).getFeatures(request)

    def capabilities(self):
        c=Qgis.VectorProviderCapability
        return (c.AddFeatures|c.DeleteFeatures|c.ChangeAttributeValues|c.ChangeGeometries|c.ChangeFeatures|
                c.SelectAtId|c.ReloadData)

    def defaultValue(self,fieldIndex):
        # A new feature gets its persistent identity when it is created, so a
        # retried save sends the same identity instead of a second feature.
        if fieldIndex==self._id_index: return str(uuid4())
        # The repository applies no default: the model's literal default is
        # pre-filled here (an expression default is ignored).
        if self.rules is not None and self._id_index<fieldIndex<=len(self._specs)+self._id_index:
            spec=self._specs[fieldIndex-1-self._id_index]
            found,value=self.rules.default(spec['name'])
            if found:
                try: return values.from_model(spec,value)
                except ValueError: return None
        return None

    def reloadProviderData(self):
        self.reload_from_service()

    def _data_changed(self):
        if self._reloading: return
        try:
            self.reload_from_service()
        except (ServiceError,ValueError,sqlite3.Error) as error:
            self.pushError('Recarga pelo serviço falhou: '+str(error))

    def reload_from_service(self):
        """Read the service state again (after a stale refusal or an undo, for instance)."""
        if not self._cache or self._reloading: return
        self._reloading=True
        try:
            self._loader.reset(None)
            self._fill_initial()
            self._refusal=None
        finally:
            self._reloading=False

    @property
    def loads(self):
        """Times the cache was (re)initialized from the service: opening, reloads, invalidations."""
        return self._loader.resets if self._loader else 0

    @property
    def read_stats(self):
        loader=self._loader
        return {'cache':'ogr' if getattr(self._cache,'native',False) else 'python',
                'full_reads':loader.full_reads,'region_reads':loader.region_reads,'pages':loader.pages,
                'resets':loader.resets,'regions':len(loader.regions),'full':loader.full} if loader else {}

    @property
    def generation(self): return self._loader.generation if self._loader else None

    def _effective_generation(self):
        """The generation this layer's cache is consistent with, past sibling layers' own writes."""
        return self._loader.follow()

    @property
    def source_uri(self): return self._uri

    @property
    def last_violations(self):
        """What the repository model refused in the last refused save, found
        here or by the service: `{dataset, id, field, code, detail}` each."""
        return [dict(item) for item in self._violations]

    def _check_model(self,dsg_id,properties):
        """Refuse a state the repository model does not accept (the codes and reasons of the service)."""
        if self.rules is None or not self.model_check: return
        found=self.rules.check(dsg_id,{name:values.plain(value) for name,value in properties.items()})
        if found:
            raise LocalRefusal(' '.join(model_rules.report(found)),violations=found)

    # Saving --------------------------------------------------------------------

    def prepare_save(self,layer):
        """Validate the whole edit buffer before QGIS calls the write methods.

        Connected to `beforeCommitChanges` by `attach_layer`. On any problem
        the save is refused as a whole: every write method then returns
        False and nothing reaches the service. The whole buffer is also sent
        here, in one request."""
        self._refusal=None; self._violations=[]
        self._save=SaveRecord(hooked=True,generation_before=self.generation); self._log_save()
        buffer=layer.editBuffer()
        if buffer is None: return
        try:
            connection=self._connection(); self._save.actor=connection.actor()
            problems=[]; found=[]
            planned=[]
            def check(action):
                try: planned.append(action())
                except LocalRefusal as error: problems.append(str(error)); found.extend(error.violations)
                except ValueError as error: problems.append(str(error))
            geometries=buffer.changedGeometries(); attributes=buffer.changedAttributeValues()
            deleted={fid for fid in buffer.deletedFeatureIds() if fid>=0}
            for fid in sorted(set(geometries)|set(attributes)):
                if fid<0 or fid in deleted: continue
                check(lambda fid=fid:self._plan_change(fid,attributes.get(fid,{}),geometries.get(fid)))
            for fid,feature in sorted(buffer.addedFeatures().items()):
                check(lambda feature=feature:self._plan_add(feature))
            for fid in sorted(deleted):
                check(lambda fid=fid:self._plan_delete(fid))
            if problems:
                raise LocalRefusal('Salvamento recusado antes de enviar; nada foi gravado. '+' '.join(problems[:20])+
                                   (' E mais '+str(len(problems)-20)+' problema(s).' if len(problems)>20 else ''),violations=found)
            self._send_batch(connection,self._save.actor,planned)
            self._save.sent=True
            return
        except ServiceError as error:
            self._violations=list(error.violations)
            self._refusal=('stale' if self._is_stale(error) else 'refused',self._batch_failure(error))
        except ValueError as error:
            self._violations=list(getattr(error,'violations',None) or [])
            self._refusal=('local',str(error))
        if self._refusal:
            events.saveReport.emit(self._uri,self._refusal[0],self._refusal[1])

    def finish_save(self):
        """End of a commit (afterCommitChanges/afterRollBack): later direct write calls are their own saves."""
        if self._save is not None: self._save.finished=True

    def _stale_message(self,current=None):
        seen=str(self.generation)
        return ('A atividade mudou no serviço depois da leitura desta camada (geração vista '+seen+
                (', atual '+str(current) if current is not None else '')+'). Nada mais foi gravado. '
                'Use "Recarregar camada" para ler o estado atual; as edições pendentes continuam no buffer '
                'e podem ser salvas de novo sobre o estado recarregado.')

    @staticmethod
    def _is_stale(error):
        # D042: by the stable code, never by the wording of the message.
        return getattr(error,'code',None)=='stale_generation'

    @staticmethod
    def _service_message(error):
        status=getattr(error,'status',0)
        return str(error) if status else 'Serviço inacessível: '+str(error)

    def _batch_failure(self,error):
        if self._is_stale(error):
            return self._stale_message()
        if not getattr(error,'status',0):
            # No answer: the service may have written it. The same save sent
            # again carries the same request_id and is not written twice.
            return (self._service_message(error).rstrip().rstrip('.')+'. Sem resposta, não se sabe se o salvamento foi '
                    'gravado. Salve de novo sem mudar as edições: o mesmo pedido não é gravado duas vezes.')
        if getattr(error,'violations',None):
            # Refused by the repository model: one line per feature and field.
            return (model_rules.refusal_text(error.violations)+' As edições continuam no buffer e podem ser '
                    'corrigidas e salvas de novo.')
        message=self._service_message(error).rstrip()
        if not message.endswith(('.','!','?')): message+='.'
        return (message+' Nada foi gravado neste salvamento; as edições continuam no buffer e podem ser '
                'corrigidas e salvas de novo.')

    def _label(self,dsg_id):
        return 'Feição '+str(dsg_id)+' (classe '+self._parts['dataset']+')'

    def _current(self,fid):
        row=self._cache.by_fid(fid)
        if row is None:
            raise LocalRefusal('Feição de fid '+str(fid)+' não está na leitura atual da camada; recarregue a camada.')
        return row[0],values.loads(row[1])

    def api_feature(self,fid):
        """Identity and API state `{id, properties, geometry}` of a loaded feature (lineage actions of the panel)."""
        return self._current(fid)

    def geometry_to_api(self,geometry,label):
        """GeoJSON of a QGIS geometry for this class, with the checks of a save."""
        return self._geometry_to_api(geometry,label)

    def _plan_change(self,fid,attribute_changes,geometry):
        dsg_id,feature=self._current(fid)
        label=self._label(dsg_id)
        properties=dict(feature['properties'])
        for index,value in attribute_changes.items():
            index=int(index)
            if self._id_index and index==0:
                if not values.is_null(value) and int(value)!=fid:raise LocalRefusal(label+': identificador local não pode ser alterado.')
                continue
            if index==self._id_index:
                if values.is_null(value) or str(value)!=dsg_id:
                    raise LocalRefusal(label+': a identidade (dsg_id) não pode ser alterada.')
                continue
            if not self._id_index<index<=len(self._specs)+self._id_index:
                raise LocalRefusal(label+': campo '+str(index)+' inexistente.')
            spec=self._specs[index-1-self._id_index]
            try: properties[spec['name']]=values.to_api(spec,value)
            except ValueError as error: raise LocalRefusal(label+': '+str(error)) from None
        self._check_model(dsg_id,properties)
        desired={'id':dsg_id,'properties':properties,'geometry':feature['geometry']}
        if geometry is not None:
            desired['geometry']=self._geometry_to_api(geometry,label)
        return Operation('put',dsg_id,desired)

    def _plan_delete(self,fid):
        dsg_id,_=self._current(fid)
        return Operation('delete',dsg_id)

    def _plan_add(self,qgs_feature):
        attributes=qgs_feature.attributes()
        dsg_id=attributes[self._id_index] if len(attributes)>self._id_index else None
        if values.is_null(dsg_id) or not str(dsg_id).strip():
            dsg_id=self._added_ids.get(qgs_feature.id())
            if dsg_id is None:
                dsg_id=str(uuid4())
                self._added_ids[qgs_feature.id()]=dsg_id
        dsg_id=str(dsg_id)
        label=self._label(dsg_id)
        if not model_rules.is_canonical_uuid(dsg_id):
            detail='a identidade '+json.dumps(dsg_id,ensure_ascii=False)+' não é um UUID em texto canônico (36 caracteres, hexadecimal minúsculo, com hífens), como toda identidade persistente (D040)'
            raise LocalRefusal(label+': '+detail+' [identity_form].',
                               violations=[{'dataset':self._parts['dataset'],'id':dsg_id,'field':None,'code':'identity_form','detail':detail}])
        properties={}
        for index,spec in enumerate(self._specs,start=1+self._id_index):
            value=attributes[index] if index<len(attributes) else None
            try: properties[spec['name']]=values.to_api(spec,value)
            except ValueError as error: raise LocalRefusal(label+': '+str(error)) from None
        self._check_model(dsg_id,properties)
        geometry=None
        if qgs_feature.hasGeometry():
            geometry=self._geometry_to_api(qgs_feature.geometry(),label)
        elif self._geometry_type is None:
            geometry=None
        return Operation('put',dsg_id,{'id':dsg_id,'properties':properties,'geometry':geometry},added_fid=qgs_feature.id())

    def _geometry_to_api(self,geometry,label):
        if geometry is None or geometry.isNull():
            return None
        if self._geometry_type is None:
            raise LocalRefusal(label+': a classe não tem geometria.')
        if geometry.isEmpty():
            raise LocalRefusal(label+': geometria vazia; use NULL para ausência.')
        candidate=QgsGeometry(geometry)
        if self._geometry_type.startswith('Multi') and not candidate.isMultipart():
            candidate.convertToMultiType()
        elif not self._geometry_type.startswith('Multi') and candidate.isMultipart():
            if not candidate.convertToSingleType():
                raise LocalRefusal(label+': geometria com várias partes numa classe '+self._geometry_type+'.')
        try:
            value,z=values.wkb_to_geojson(bytes(candidate.asWkb()))
        except ValueError as error:
            raise LocalRefusal(label+': '+str(error)) from None
        if value['type']!=self._geometry_type:
            raise LocalRefusal(label+': tipo geométrico '+value['type']+' difere do schema ('+self._geometry_type+').')
        if z!=self._z:
            raise LocalRefusal(label+': a classe '+('exige' if self._z else 'não aceita')+' coordenada Z.')
        if not candidate.isGeosValid():
            reasons='; '.join(e.what() for e in candidate.validateGeometry(Qgis.GeometryValidationEngine.Geos)[:3])
            raise LocalRefusal(label+': geometria inválida'+(' ('+reasons+')' if reasons else '')+'.')
        return value

    def _confirming(self):
        """The hook already sent this save in one batch: write calls only confirm."""
        return self._save is not None and self._save.hooked and self._save.sent and not self._save.finished

    def _begin_call(self):
        """Start or continue the save record; return (connection, actor) or raise."""
        if self._refusal:
            raise LocalRefusal(self._refusal[1],announced=True)
        if self._save is None or not self._save.hooked or self._save.finished:
            # Without the beforeCommitChanges hook each write call is its own save.
            self._save=SaveRecord(hooked=False,generation_before=self.generation); self._log_save()
            self._violations=[]
        elif self._save.failed:
            # A refusal already stopped this save: later steps of the same
            # commit (deletions, additions) are not sent.
            raise LocalRefusal('Salvamento interrompido pela recusa anterior; as demais alterações não foram enviadas e continuam no buffer.',announced=True)
        connection=self._connection()
        actor=connection.actor()
        self._save.actor=actor
        return connection,actor

    def _report(self,kind,message):
        self.pushError(message)
        events.saveReport.emit(self._uri,kind,message)

    def _send(self,operations):
        """Send the operations of one write call, in one batch."""
        connection,actor=self._begin_call()
        try:
            self._send_batch(connection,actor,operations)
        except ServiceError as error:
            self._save.failed.append(('',self._service_message(error)))
            self._violations=list(error.violations)
            self._report('stale' if self._is_stale(error) else 'refused',self._batch_failure(error))
            return False
        return True

    def _send_batch(self,connection,actor,operations):
        """One POST /features for every operation: all written, or nothing (D026)."""
        record=self._save
        inserts=[]; updates=[]; deletes=[]; before={}
        for operation in operations:
            row=self._cache.by_id(operation.dsg_id)
            if operation.verb=='put' and row is not None and row[1]==values.dumps(operation.feature):
                record.skipped.append(operation.dsg_id); continue
            if operation.verb=='delete':
                if row is None: record.skipped.append(operation.dsg_id); continue
                deletes.append(operation.dsg_id)
            elif row is None:
                inserts.append(operation.feature)
            else:
                updates.append(operation.feature)
            before[operation.dsg_id]=(operation.verb,row[1] if row else None)
        if not before:
            return None
        # D044: the limit the service announces, checked before sending.
        most=connection.limits().get('batch_operations')
        operations_sent=len(inserts)+len(updates)+len(deletes)
        if isinstance(most,int) and operations_sent>most:
            raise LocalRefusal('Salvamento com '+str(operations_sent)+' operações excede o limite do serviço ('+
                               str(most)+' por salvamento); salve as edições em partes menores.')
        expected=self._effective_generation()
        body={'dataset':self._parts['dataset'],'expected_generation':expected,
              'inserts':inserts,'updates':updates,'deletes':deletes}
        # SAP 3.0: the identity of the save is the login of the SAP token.
        if actor: body['actor']=actor
        # The same save sent again (lost response) keeps its key.
        key=values.dumps([self._parts['repo'],body])
        body=dict(body,request_id=self._save_keys.setdefault(key,str(uuid4())))
        try:
            result=values.loads(connection.client.request_text(self._path('/features'),values.dumps(body),'POST'))
        except ServiceError as error:
            # An answer from the service settles the key; only an unreachable
            # service (no status) may have written without answering.
            if getattr(error,'status',0): self._save_keys.pop(key,None)
            raise
        self._save_keys.pop(key,None)
        generation=int(result['generation'])
        repository_state(self._parts['service'],self._parts['repo']).record(expected,generation,self._parts['dataset'],self._writer)
        with self._loader.lock:
            self._loader.generation=generation
        record.generation_after=generation; record.revision=result.get('revision')
        record.written.extend((verb,dsg_id,state) for dsg_id,(verb,state) in before.items())
        for dsg_id in deletes: self._cache.remove(dsg_id)
        self._count+=len(inserts)-len(deletes)
        self._refresh_many(connection,[f for f in inserts+updates])
        return result

    def _refresh_many(self,connection,features):
        """Store the canonical states the service kept; the sent states if they cannot be read back,
        and then say so: the map shows what was sent, not what was stored, until the layer is reloaded."""
        sent={str(f['id']):f for f in features}
        ids=sorted(sent)
        unread=0
        for start in range(0,len(ids),REFRESH_CHUNK):
            chunk=ids[start:start+REFRESH_CHUNK]
            try:
                page=values.loads(connection.client.request_text(self._path('/features')+query(
                    dataset=self._parts['dataset'],ids=json.dumps(chunk),limit=500,map_geometry='false')))
                stored={str(item['feature']['id']):item['feature'] for item in page['items']}
            except ServiceError as error:
                stored={}
                unread+=len(chunk)
                QgsMessageLog.logMessage('Releitura depois do salvamento falhou: '+str(error),LOG_TAG,Qgis.MessageLevel.Warning)
            for dsg_id in chunk:
                feature=stored.get(dsg_id,sent[dsg_id])
                row=cache_row(feature,self._z)
                self._cache.put(*row)
                if row[3] and not self._extent.isNull():
                    self._extent.combineExtentWith(QgsRectangle(*row[3]))
                elif row[3]:
                    self._extent=QgsRectangle(*row[3])
        if unread:
            self.pushError('O salvamento foi gravado, mas a releitura do estado gravado falhou para '+str(unread)+
                           ' feição(ões): o mapa mostra o estado enviado, que pode diferir do gravado. Recarregue a camada.')

    def _run(self,build):
        if self._confirming():
            return True
        if self._refusal:
            # The whole save was already refused (and announced) by the hook:
            # QGIS shows that message, with every problem, not the first one.
            self.pushError(self._refusal[1]); return False
        try:
            operations=build()
            return self._send(operations)
        except LocalRefusal as error:
            if getattr(error,'announced',False): self.pushError(str(error))
            else:
                self._violations=list(error.violations)
                self._report('local',str(error))
            return False
        except ServiceError as error:
            self._report('stale' if self._is_stale(error) else 'refused',self._service_message(error)); return False
        except ValueError as error:
            self._report('local',str(error)); return False

    def changeFeatures(self,attr_map,geometry_map):
        def build():
            operations=[]
            for fid in sorted(set(attr_map)|set(geometry_map)):
                operations.append(self._plan_change(fid,attr_map.get(fid,{}),geometry_map.get(fid)))
            return operations
        return self._run(build)

    def changeAttributeValues(self,attr_map):
        return self.changeFeatures(attr_map,{})

    def changeGeometryValues(self,geometry_map):
        return self.changeFeatures({},geometry_map)

    def deleteFeatures(self,ids):
        def build():
            operations=[]
            for fid in sorted(ids):
                row=self._cache.by_fid(fid)
                if row is not None: operations.append(Operation('delete',row[0]))
            return operations
        return self._run(build)

    def addFeatures(self,flist,flags=None):
        features=list(flist)
        if self._confirming():
            # Sent by the hook: give each added feature the fid of its identity.
            for feature in features:
                attributes=feature.attributes()
                dsg_id=attributes[self._id_index] if len(attributes)>self._id_index and not values.is_null(attributes[self._id_index]) else self._added_ids.get(feature.id())
                row=self._cache.by_id(str(dsg_id)) if dsg_id is not None else None
                if row is None:
                    self.pushError('Feição adicionada sem leitura de volta do serviço; recarregue a camada.')
                    return False,features
                feature.setId(row[0])
                if attributes: feature.setAttribute(self._id_index,str(dsg_id))
                if self._id_index:feature.setAttribute(0,row[0])
                self._added_ids.pop(feature.id(),None)
            return True,features
        planned=[]
        def build():
            planned.extend(self._plan_add(feature) for feature in features)
            return planned
        if not self._run(build):
            return False,features
        for feature,operation in zip(features,planned):
            row=self._cache.by_id(operation.dsg_id)
            if row is not None:
                feature.setId(row[0])
                if feature.attributes(): feature.setAttribute(self._id_index,operation.dsg_id)
                if self._id_index:feature.setAttribute(0,row[0])
            self._added_ids.pop(operation.added_fid,None)
        return True,features

    # D026 ------------------------------------------------------------------------

    def _log_save(self):
        self.save_log.append(self._save)
        del self.save_log[:-20]

    def last_save(self):
        return self._save

    def undo_last_save(self):
        """Undo the last save of the live clone (D026, "desfazer salvamento").

        The service restores the states every identity of its last save had
        before it, as a new save by the declared actor, and refuses after
        the merge or when there is nothing to undo; its message is raised as
        ServiceError. The cache is read again afterwards, so this layer shows
        the restored states. Other layers of the same activity see a foreign
        change and read again at their next access or save."""
        connection=self._connection()
        body={'expected_generation':self._effective_generation()}
        if connection.actor(): body['actor']=connection.actor()
        result=connection.client.request(self._path('/undo'),body,'POST')
        self.reload_from_service()
        return result


# Registration -------------------------------------------------------------------

_metadata=None


def register_provider():
    """Register the provider once per QGIS session (QGIS has no unregister).

    The former DSG Versioning plugin is retired: when it (or an older copy of
    this module) already holds the key, nothing is registered again and the
    layers keep opening with the provider QGIS already has."""
    global _metadata
    registry=QgsProviderRegistry.instance()
    if PROVIDER_KEY in registry.providerList():
        if _metadata is None:
            QgsMessageLog.logMessage('O provedor '+PROVIDER_KEY+' já estava registrado por outro plugin; o plugin do SAP usa o registrado.',
                                     LOG_TAG,Qgis.MessageLevel.Warning)
        return False
    _metadata=QgsProviderMetadata(PROVIDER_KEY,DsgVersioningProvider.description(),DsgVersioningProvider.createProvider)
    return registry.registerProvider(_metadata)


def attach_layer(layer):
    """Validate (and, with batch writes, send) the whole buffer before QGIS writes it (see `prepare_save`)."""
    if layer.providerType()!=PROVIDER_KEY or layer.property('dsg_versioning_attached'):
        return
    if getattr(layer.dataProvider()._cache,'native',False):
        layer.setEditorWidgetSetup(0,QgsEditorWidgetSetup('Hidden',{}))
        config=layer.editFormConfig();config.setReadOnly(0,True);layer.setEditFormConfig(config)
    def before(_stop_editing,layer=layer):
        provider=layer.dataProvider()
        if hasattr(provider,'prepare_save'): provider.prepare_save(layer)
    def after(*_args,layer=layer):
        provider=layer.dataProvider()
        if hasattr(provider,'finish_save'): provider.finish_save()
    layer.beforeCommitChanges.connect(before)
    layer.afterCommitChanges.connect(after)
    layer.afterRollBack.connect(after)
    layer.setProperty('dsg_versioning_attached',True)
