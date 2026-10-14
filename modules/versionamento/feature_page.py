"""DSGP/1 decoder, independent of QGIS and third-party modules.

Offsets and sizes are checked before reconstructing any feature. This first
adapter keeps the provider's established JSON value contract; WKB is returned
alongside it for caches which can consume it directly.
"""
import json
import math
import re
import struct

MEDIA_TYPE = 'application/vnd.dsg.features.v1'
TYPES = [None, 'Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon']


def _strict_json(text):
    def reject(value):
        raise ValueError('Número JSON não finito: '+value)
    return json.loads(text,parse_constant=reject)


def decode(data, parse_attributes=_strict_json, materialize_geometry=True):
    try:
        return _decode(data,parse_attributes,materialize_geometry)
    except (KeyError,TypeError,IndexError,OverflowError,struct.error,AttributeError,RecursionError) as error:
        raise ValueError('Página binária inválida ou incompatível.') from error


def _decode(data, parse_attributes, materialize_geometry):
    def require(condition):
        if not condition:
            raise ValueError('Página binária inválida ou incompatível.')

    require(8 <= len(data) <= 2097152 and data[:4] == b'DSGP')
    length, = struct.unpack_from('<I', data, 4)
    base = 8 + length
    require(length % 8 == 0 and base <= len(data))
    head = _strict_json(data[8:base].decode('utf-8-sig'))
    n = head.get('count')
    require(type(head.get('version')) is int and head['version'] == 1 and type(n) is int and 0 <= n <= 500)
    require(type(head.get('generation')) is int and head['generation'] >= 0)
    require(isinstance(head.get('dataset'), str) and (head.get('next') is None or isinstance(head['next'], str)))
    require(isinstance(head.get('schema'),str) and re.fullmatch('[0-9a-f]{64}',head['schema']) is not None)
    ranges = []

    def section(s, width=1):
        require(isinstance(s, list) and len(s) == 2 and all(type(v) is int and v >= 0 for v in s))
        offset, size = s
        require(offset % 8 == 0 and size % width == 0 and base + offset + size <= len(data))
        if size:
            require(not any(offset < end and start < offset + size for start, end in ranges))
            ranges.append((offset, offset + size))
        return memoryview(data)[base+offset:base+offset+size]

    attrs = parse_attributes(bytes(section(head['attributes'])).decode('utf-8-sig'))
    require(isinstance(attrs.get('ids'), list) and len(attrs['ids']) == n and all(isinstance(i, str) for i in attrs['ids']))
    require(len(set(attrs['ids'])) == n and isinstance(attrs.get('columns'), dict))
    require(all(isinstance(c, list) and len(c) == n for c in attrs['columns'].values()))

    def geometry(g):
        require(isinstance(g, dict))
        kind, dims, encoding = g.get('type'), g.get('dimensions'), g.get('encoding')
        require(type(kind) is int and 0 <= kind <= 6 and dims in (2, 3) and type(g.get('srid')) is int)
        require(encoding in ('f64', 'delta-i32', 'delta-i64'))
        require(encoding == 'f64' or (dims == 2 and g['srid'] in (4326, 4674)))
        fmt = {'f64': '<d', 'delta-i32': '<i', 'delta-i64': '<q'}[encoding]
        raw = section(g['coordinates'], struct.calcsize(fmt))
        values = list(struct.unpack('<'+str(len(raw)//struct.calcsize(fmt))+fmt[-1],raw))
        require(len(values) % dims == 0 and len(values)//dims <= 100000)
        ring, part, feature = [[v[0] for v in struct.iter_unpack('<I', section(g[key], 4))] for key in ('rings','parts','features')]
        for offsets, end in ((ring,len(values)//dims),(part,len(ring)-1),(feature,len(part)-1)):
            require(bool(offsets) and offsets[0] == 0 and offsets[-1] == end)
            require(all(a <= b for a,b in zip(offsets,offsets[1:])))
        require(len(feature) == n+1)
        require(all(a < b for a,b in zip(ring,ring[1:])) and all(a < b for a,b in zip(part,part[1:])))
        if encoding != 'f64':
            for a,b in zip(ring,ring[1:]):
                x=y=0
                for i in range(a*2,b*2,2):
                    x+=values[i];y+=values[i+1]
                    require(abs(x)<=1800000000 and abs(y)<=1800000000)
                    values[i]=x/1e7;values[i+1]=y/1e7
        else:require(all(math.isfinite(v) for v in values))
        geometries, blobs, bounds = [], [], []
        for a,b in zip(feature,feature[1:]):
            if a == b:
                geometries.append(None); blobs.append(None); bounds.append(None); continue
            require(kind > 0 and (kind > 3 or b-a == 1))
            pieces = []; packed=[]; box=None
            def header(code):return struct.pack('<BI',1,code+(1000 if dims == 3 else 0))
            for p in range(a,b):
                require(kind in (3,6) or part[p+1]-part[p] == 1)
                rings = []; packed_rings=[]
                for r in range(part[p],part[p+1]):
                    count = ring[r+1]-ring[r]
                    require(count == 1 if kind in (1,4) else count >= (2 if kind in (2,5) else 4))
                    start,end=ring[r]*dims,ring[r+1]*dims
                    # The canonical ring closes in XY bits; endpoint Z may differ.
                    if kind in (3,6):require(struct.pack('<2d',*values[start:start+2])==struct.pack('<2d',*values[end-dims:end-dims+2]))
                    if materialize_geometry:rings.append([values[i:i+dims] for i in range(start,end,dims)])
                    packed_rings.append((b'' if kind in (1,4) else struct.pack('<I',count))+struct.pack('<'+str(end-start)+'d',*values[start:end]))
                    # Bounded strided slices let C scan each ring, avoiding four
                    # Python min/max calls and one list allocation per vertex.
                    xs,ys=values[start:end:dims],values[start+1:end:dims]
                    current=[min(xs),min(ys),max(xs),max(ys)]
                    box=current if box is None else [min(box[0],current[0]),min(box[1],current[1]),max(box[2],current[2]),max(box[3],current[3])]
                if materialize_geometry:pieces.append(rings)
                simple=kind if kind<=3 else kind-3
                packed.append(header(simple)+(struct.pack('<I',len(packed_rings)) if simple==3 else b'')+b''.join(packed_rings))
            if materialize_geometry:
                coords = pieces[0][0][0] if kind == 1 else pieces[0][0] if kind == 2 else pieces[0] if kind == 3 else [p[0][0] for p in pieces] if kind == 4 else [p[0] for p in pieces] if kind == 5 else pieces
                geometries.append({'type': TYPES[kind], 'coordinates': coords})
            else:geometries.append(None)
            blobs.append(packed[0] if kind<=3 else header(kind)+struct.pack('<I',len(packed))+b''.join(packed))
            bounds.append(box)
        return geometries, blobs, bounds

    source, blobs, bounds = geometry(head['source'])
    mapped = geometry(head['map'])[0] if head.get('map') is not None else None
    if mapped is not None:
        require(head['map']['srid']==4326 and head['map']['type']==head['source']['type'] and head['map']['dimensions']==head['source']['dimensions'])
    require(base+max(end for _,end in ranges)==len(data))
    items = []
    for k, identity in enumerate(attrs['ids']):
        item = {'feature': {'id': identity, 'properties': {key:column[k] for key,column in attrs['columns'].items()}, 'geometry': source[k]}, '_wkb': blobs[k]}
        if not materialize_geometry:item['_bounds']=bounds[k]
        if mapped is not None: item['map_geometry'] = mapped[k]
        items.append(item)
    return {'generation': head['generation'], 'next': head['next'], 'srid': head['source']['srid'], 'items': items}
