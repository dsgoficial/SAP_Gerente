"""Exact conversions between the service API and QGIS values.

Nothing here rounds: numbers read from the service keep their source lexeme
until a field kind asks for a Python value (``int`` for 64-bit integers,
``float`` for binary64 reals, both exact from the lexeme); geometry
coordinates become WKB doubles and come back through ``repr``, the shortest
text that reads the same double.

One exception, asked by the repository model: a field marked ``single`` is a
real of 4 bytes in the source base. It is shown as the float whose shortest
text reads back to the same binary32, and a value typed by the user is
rounded to the nearest binary32 before it is saved (see model.py).
"""
from datetime import date,datetime,timezone
from decimal import Decimal,InvalidOperation
import json
import math
import struct
from uuid import UUID

from qgis.PyQt.QtCore import QByteArray,QDate,QDateTime,QTime,QTimeZone,QMetaType

from .model import float32,float32_display


class Number(str):
    """A JSON number kept as the text it was read from."""
    __slots__=()


class RawJson(str):
    """JSON text written verbatim into a request body."""
    __slots__=()


def _no_constant(name):
    raise ValueError('JSON com constante não suportada: '+name)


def loads(text):
    return json.loads(text,parse_int=Number,parse_float=Number,parse_constant=_no_constant)


def dumps(value):
    out=[]
    _dump(value,out)
    return ''.join(out)


def _dump(value,out):
    if value is None: out.append('null')
    elif value is True: out.append('true')
    elif value is False: out.append('false')
    elif isinstance(value,(Number,RawJson)): out.append(str(value))
    elif isinstance(value,str): out.append(json.dumps(value,ensure_ascii=False))
    elif isinstance(value,int): out.append(str(int(value)))
    elif isinstance(value,float):
        if not math.isfinite(value): raise ValueError('Número não finito não é aceito pelo serviço.')
        out.append(repr(value))
    elif isinstance(value,dict):
        out.append('{')
        for index,(key,item) in enumerate(value.items()):
            if index: out.append(',')
            out.append(json.dumps(str(key),ensure_ascii=False)); out.append(':'); _dump(item,out)
        out.append('}')
    elif isinstance(value,(list,tuple)):
        out.append('[')
        for index,item in enumerate(value):
            if index: out.append(',')
            _dump(item,out)
        out.append(']')
    else:
        raise ValueError('Valor sem forma JSON: '+type(value).__name__)


def plain(value):
    """Python value of something read with `loads` or built for a request:
    number lexemes become int or float, verbatim JSON is parsed."""
    if isinstance(value,RawJson): return json.loads(value)
    if isinstance(value,Number):
        try: return int(value)
        except ValueError: return float(value)
    if isinstance(value,dict): return {key:plain(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)): return [plain(item) for item in value]
    return value


# Geometry -------------------------------------------------------------------

GEOMETRY_CODES={'Point':1,'LineString':2,'Polygon':3,'MultiPoint':4,'MultiLineString':5,'MultiPolygon':6}
GEOMETRY_NAMES={code:name for name,code in GEOMETRY_CODES.items()}


def wkb_code(geometry_type,z):
    return GEOMETRY_CODES[geometry_type]+(1000 if z else 0)


def geojson_to_wkb(geometry,z):
    """ISO WKB (little endian) of a GeoJSON geometry, coordinates read exactly."""
    out=bytearray()
    _write_geometry(out,geometry['type'],geometry['coordinates'],z)
    return bytes(out)


def _write_point(out,point,z):
    if len(point)<2 or len(point)>3:
        raise ValueError('Coordenada GeoJSON com dimensão inválida.')
    out+=struct.pack('<dd',float(point[0]),float(point[1]))
    if z:
        out+=struct.pack('<d',float(point[2]) if len(point)==3 else math.nan)


def _write_geometry(out,kind,coordinates,z):
    if kind not in GEOMETRY_CODES:
        raise ValueError('Tipo geométrico não suportado: '+str(kind))
    out+=struct.pack('<BI',1,wkb_code(kind,z))
    if kind=='Point':
        if not coordinates: _write_point(out,[math.nan,math.nan,math.nan],z)
        else: _write_point(out,coordinates,z)
    elif kind=='LineString':
        out+=struct.pack('<I',len(coordinates))
        for point in coordinates: _write_point(out,point,z)
    elif kind=='Polygon':
        out+=struct.pack('<I',len(coordinates))
        for ring in coordinates:
            out+=struct.pack('<I',len(ring))
            for point in ring: _write_point(out,point,z)
    else:
        single=kind[5:]
        out+=struct.pack('<I',len(coordinates))
        for part in coordinates: _write_geometry(out,single,part,z)


class _Reader:
    def __init__(self,data): self.data=data; self.offset=0

    def take(self,fmt):
        values=struct.unpack_from(fmt,self.data,self.offset)
        self.offset+=struct.calcsize(fmt)
        return values


def wkb_to_geojson(data):
    """GeoJSON geometry and Z flag of ISO or extended WKB; coordinates as Python floats."""
    reader=_Reader(bytes(data))
    geometry,z=_read_geometry(reader)
    if reader.offset!=len(reader.data):
        raise ValueError('WKB com bytes excedentes.')
    return geometry,z


def _read_geometry(reader):
    order,=reader.take('<B')
    endian='<' if order==1 else '>'
    code,=reader.take(endian+'I')
    z=m=False
    if code&0x80000000: z=True
    if code&0x40000000: m=True
    code&=0x0FFFFFFF
    if 1000<=code<2000: z=True; code-=1000
    elif 2000<=code<3000: m=True; code-=2000
    elif 3000<=code<4000: z=m=True; code-=3000
    if m:
        raise ValueError('Geometria com medida (M) não é aceita pelo serviço.')
    if code not in GEOMETRY_NAMES:
        raise ValueError('Geometria curva ou coleção não é aceita pelo serviço; converta para '+', '.join(GEOMETRY_CODES)+'.')
    kind=GEOMETRY_NAMES[code]
    width=3 if z else 2
    def point():
        return [float(v) for v in reader.take(endian+'d'*width)]
    if kind=='Point':
        coordinates=point()
        if all(math.isnan(v) for v in coordinates): coordinates=[]
    elif kind=='LineString':
        count,=reader.take(endian+'I'); coordinates=[point() for _ in range(count)]
    elif kind=='Polygon':
        rings,=reader.take(endian+'I'); coordinates=[]
        for _ in range(rings):
            count,=reader.take(endian+'I'); coordinates.append([point() for _ in range(count)])
    else:
        parts,=reader.take(endian+'I'); coordinates=[]
        for _ in range(parts):
            part,part_z=_read_geometry(reader)
            if part_z!=z or part['type']!=kind[5:]:
                raise ValueError('Coleção com partes de tipo ou dimensão diferentes.')
            coordinates.append(part['coordinates'])
    for value in _flatten(coordinates):
        if not math.isfinite(value):
            raise ValueError('Coordenada não finita não é aceita pelo serviço.')
    return {'type':kind,'coordinates':coordinates},z


def _flatten(coordinates):
    for item in coordinates:
        if isinstance(item,list): yield from _flatten(item)
        else: yield item


def bounds(geometry):
    xs=[];ys=[]
    def walk(coordinates):
        if coordinates and not isinstance(coordinates[0],list):
            xs.append(float(coordinates[0])); ys.append(float(coordinates[1]))
        else:
            for item in coordinates: walk(item)
    walk(geometry['coordinates'])
    if not xs: return None
    return min(xs),min(ys),max(xs),max(ys)


# Attribute kinds ----------------------------------------------------------------

def field_type(spec):
    """(QMetaType, typeName, length, precision, comment) of an API field."""
    kind=spec['kind']
    if kind=='integer': return QMetaType.Type.LongLong,'integer',0,0,'inteiro de 64 bits'
    if kind=='real': return QMetaType.Type.Double,'real',0,0,'real de 4 bytes na base de origem' if spec.get('single') else 'binary64'
    if kind=='boolean': return QMetaType.Type.Bool,'boolean',0,0,''
    if kind=='date': return QMetaType.Type.QDate,'date',0,0,'data'
    if kind=='datetime':
        precision=spec.get('precision')
        if precision is not None and int(precision)>3:
            # QDateTime keeps milliseconds only; finer precision stays as text.
            return QMetaType.Type.QString,'datetime',0,0,'instante UTC com '+str(precision)+' casas, como texto'
        return QMetaType.Type.QDateTime,'datetime',0,0,'instante UTC'
    if kind=='bytes': return QMetaType.Type.QByteArray,'bytes',0,0,'bytes'
    if kind=='decimal':
        detail=' '.join(key+'='+str(spec[key]) for key in ('precision','scale') if spec.get(key) is not None)
        return QMetaType.Type.QString,'decimal',0,0,('decimal exato como texto '+detail).strip()
    if kind=='json': return QMetaType.Type.QString,'json',0,0,'JSON como texto, lexemas preservados'
    if kind=='uuid': return QMetaType.Type.QString,'uuid',0,0,'UUID'
    return QMetaType.Type.QString,'text',0,0,''


def is_null(value):
    if value is None: return True
    is_null_method=getattr(value,'isNull',None)
    if callable(is_null_method) and not isinstance(value,(QDate,QDateTime,QByteArray)):
        return bool(is_null_method())
    if isinstance(value,(QDate,QDateTime)): return not value.isValid()
    return False


def _moment(text):
    moment=datetime.fromisoformat(text.replace('Z','+00:00'))
    if moment.tzinfo is None: moment=moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)


def to_qgis(spec,value):
    """QGIS attribute of an API value (as read with `loads`)."""
    if value is None: return None
    kind=spec['kind']
    if kind=='integer': return int(value)
    if kind=='real':
        number=float(value)
        if spec.get('single'):
            try: return float32_display(number)
            except ValueError: return number
        return number
    if kind=='boolean': return bool(value)
    if kind=='json': return dumps(value)
    if kind=='date':
        day=date.fromisoformat(str(value)); return QDate(day.year,day.month,day.day)
    if kind=='datetime':
        if field_type(spec)[0]==QMetaType.Type.QString: return str(value)
        moment=_moment(str(value))
        return QDateTime(QDate(moment.year,moment.month,moment.day),
                         QTime(moment.hour,moment.minute,moment.second,moment.microsecond//1000),QTimeZone.utc())
    if kind=='bytes': return QByteArray.fromHex(str(value).encode('ascii'))
    return str(value)


def to_api(spec,value):
    """API value of a QGIS attribute; refuses rather than rounding."""
    name=spec['name']
    if is_null(value):
        if spec.get('nullable') is False:
            raise ValueError(name+': valor obrigatório.')
        return None
    kind=spec['kind']
    def refuse(detail=''):
        return ValueError(name+': valor incompatível com '+kind+(' ('+detail+')' if detail else '')+'.')
    if kind=='integer':
        if isinstance(value,bool): raise refuse()
        if isinstance(value,float):
            if not value.is_integer(): raise refuse('número com fração')
            value=int(value)
        if isinstance(value,str):
            try: value=int(value.strip())
            except ValueError: raise refuse() from None
        if not isinstance(value,int) or not -(2**63)<=value<2**63: raise refuse('fora de 64 bits')
        return int(value)
    if kind=='real':
        if isinstance(value,bool): raise refuse()
        try: number=float(value)
        except (TypeError,ValueError): raise refuse() from None
        if not math.isfinite(number): raise refuse('não finito')
        if spec.get('single'):
            try: number=float32(number)
            except ValueError as error: raise refuse(str(error)) from None
        return 0.0 if number==0 else number
    if kind=='boolean':
        if isinstance(value,bool): return value
        if isinstance(value,int) and value in (0,1): return bool(value)
        raise refuse()
    if kind=='json':
        text=value if isinstance(value,str) else dumps(value)
        try: loads(text)
        except ValueError as error: raise refuse('JSON inválido: '+str(error)) from None
        return RawJson(text.strip())
    if kind=='uuid':
        try: return str(UUID(str(value)))
        except ValueError: raise refuse() from None
    if kind=='decimal':
        text=str(value).strip()
        try: finite=Decimal(text).is_finite()
        except InvalidOperation: finite=False
        if not finite: raise refuse()
        return text
    if kind=='date':
        if isinstance(value,QDate): return value.toString('yyyy-MM-dd')
        try: return date.fromisoformat(str(value)).isoformat()
        except ValueError: raise refuse() from None
    if kind=='datetime':
        if isinstance(value,QDateTime):
            utc=value.toUTC(); day=utc.date(); time=utc.time()
            precision=spec.get('precision'); precision=3 if precision is None else int(precision)
            millis=time.msec()
            if precision<3 and millis%(10**(3-precision)):
                raise refuse('milissegundos além da precisão declarada de '+str(precision)+' casas')
            text='%04d-%02d-%02dT%02d:%02d:%02d'%(day.year(),day.month(),day.day(),time.hour(),time.minute(),time.second())
            if precision>0: text+='.'+('%03d'%millis)[:precision]
            return text+'Z'
        text=str(value).strip()
        try: _moment(text)
        except ValueError: raise refuse() from None
        return text
    if kind=='bytes':
        if isinstance(value,QByteArray): return bytes(value).hex()
        if isinstance(value,(bytes,bytearray)): return bytes(value).hex()
        try: return bytes.fromhex(str(value)).hex()
        except ValueError: raise refuse() from None
    if not isinstance(value,str): value=str(value)
    return value


def from_model(spec,value):
    """QGIS attribute of a literal of the repository model (a default value)."""
    kind=spec['kind']
    if value is None: return None
    if kind=='integer' and isinstance(value,int) and not isinstance(value,bool): return int(value)
    if kind=='real' and isinstance(value,(int,float)) and not isinstance(value,bool): return to_qgis(spec,float(value))
    if kind=='boolean' and isinstance(value,bool): return value
    if kind=='json': return json.dumps(value,ensure_ascii=False)
    if isinstance(value,str): return to_qgis(spec,value)
    raise ValueError(spec['name']+': valor padrão incompatível com '+kind+'.')
