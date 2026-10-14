"""Cliente do serviço de versionamento PELO SAP 3.0 (só biblioteca padrão).

Portado de `versionamento/qgis_plugin/dsg_versioning_qgis/client.py`. Muda só o
endereço e a credencial: o QGIS não fala mais com o serviço, fala com o repasse
do SAP (`<servidor SAP>/api/versionamento/servico`), que repassa para
`VERSIONAMENTO_URL/api/*` e põe ele mesmo o segredo do serviço e o `X-Dsg-Actor`
(o login do token). O cliente manda `Authorization: Bearer <token do SAP>`, o
mesmo token das outras chamadas do plugin, e nenhum `actor` próprio.

O token é lido a cada pedido (`token` pode ser uma função), porque o SAP o
renova no novo login; um 401 chama `reauth` uma vez e repete o pedido.
O JSON do Python preserva os inteiros de 64 bits com sinal.
"""
import json
import gzip
import io
import zlib
from urllib.error import HTTPError
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,urlopen

# Rota do repasse no SAP (contrato-sap.md, seção 5).
SERVICE_ROUTE='/api/versionamento/servico'


class ServiceError(ValueError):
    """Recusa ou falha do serviço, com o status HTTP (0 quando inacessível).

    `violations` lista o que o modelo do repositório (ou a permissão da etapa,
    código `permission`) recusou num salvamento (`{dataset, id, field, code,
    detail}` cada), vazia para outro erro. `code` é o código estável do
    serviço, sobre o qual o plugin decide; a mensagem só se mostra."""
    def __init__(self,message,status=0,violations=None,code=None):
        super().__init__(message)
        self.status=status
        self.violations=list(violations or [])
        self.code=code


def check_url(url):
    """Base do repasse: http(s)://servidor[:porta]/caminho, sem credencial, consulta ou fragmento."""
    parsed=urlsplit(str(url or ''))
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Use o endereço HTTP do repasse do SAP (http://servidor/api/versionamento/servico), sem credenciais.')
    return str(url).rstrip('/')


def service_base(sap_server):
    """Base do repasse a partir do servidor do SAP (com ou sem o `/api` final)."""
    server=str(sap_server or '').rstrip('/')
    if server.endswith('/api'): server=server[:-4]
    return check_url(server+SERVICE_ROUTE)


def _refusal(error,limit=1024*1024):
    """(mensagem, código, violações) de uma resposta de erro do serviço ou do SAP."""
    violations=None; code=None
    try:
        answer=json.loads(error.read(limit))
        message=answer.get('error') or answer.get('message')
        if not isinstance(message,str): raise KeyError('error')
        code=answer.get('code') if isinstance(answer.get('code'),str) else None
        listed=answer.get('violations')
        if isinstance(listed,list): violations=[item for item in listed if isinstance(item,dict)]
    except (ValueError,KeyError,TypeError,AttributeError,RecursionError):
        message='Falha HTTP '+str(error.code)
    return message,code,violations


class Client:
    def __init__(self,url,token='',reauth=None):
        self.url=check_url(url)
        self._token=token
        self._reauth=reauth
        self.binary_features=False

    @property
    def token(self):
        value=self._token() if callable(self._token) else self._token
        return (value or '').strip()

    def _headers(self,extra=None):
        headers=dict(extra or {})
        token=self.token
        if token: headers['Authorization']='Bearer '+token
        return headers

    def _retry(self,error):
        """Um 401 com renovação de login disponível: renova e diz se vale repetir."""
        if error.code!=401 or not callable(self._reauth): return False
        try: return bool(self._reauth())
        except Exception: return False

    def request_text(self,path,body_text=None,method=None,timeout=30):
        """Manda `body_text` (JSON já serializado) e devolve o texto da resposta."""
        data=None if body_text is None else body_text.encode('utf-8')
        for attempt in (0,1):
            request=Request(self.url+path,data=data,method=method or ('GET' if data is None else 'POST'),
                            headers=self._headers({'Content-Type':'application/json'}))
            try:
                with urlopen(request,timeout=timeout) as response:
                    content=response.read(32*1024*1024+1)
                    if len(content)>32*1024*1024:
                        raise ServiceError('Resposta excede orçamento do cliente; reduza a página.')
                    return content.decode('utf-8')
            except HTTPError as error:
                if attempt==0 and self._retry(error): continue
                message,code,violations=_refusal(error)
                raise ServiceError(message,error.code,violations,code) from None
            except OSError as error:
                raise ServiceError('Servidor SAP inacessível: '+str(getattr(error,'reason',error))) from None

    def request(self,path,body=None,method=None):
        text=None if body is None else json.dumps(body,ensure_ascii=False,allow_nan=False)
        result=json.loads(self.request_text(path,text,method))
        if path=='/info': self.binary_features='features_dsgp1' in result.get('capabilities',[])
        return result

    def feature_page(self,path,materialize_geometry=True):
        from . import values
        if not self.binary_features:
            try:return values.loads(self.request_text(path))
            except ServiceError:raise
            except (ValueError,RecursionError) as error:
                raise ServiceError('Página JSON recebida inválida ou incompleta: '+str(error)) from None
        from .feature_page import decode,MEDIA_TYPE
        for attempt in (0,1):
            request=Request(self.url+path+('&' if '?' in path else '?')+'format=dsgp1',
                            headers=self._headers({'Accept':MEDIA_TYPE,'Accept-Encoding':'gzip'}))
            try:
                with urlopen(request,timeout=30) as response:
                    if response.headers.get_content_type()!=MEDIA_TYPE:
                        raise ServiceError('Tipo de página incompatível com o serviço.')
                    content=response.read(2097153)
                    if len(content)>2097152: raise ServiceError('Página binária excede orçamento do cliente.')
                    coding=response.headers.get('Content-Encoding','identity')
                    if coding=='gzip':
                        with gzip.GzipFile(fileobj=io.BytesIO(content)) as stream: content=stream.read(2097153)
                    elif coding!='identity': raise ServiceError('Codificação HTTP não suportada pelo cliente.')
                    if len(content)>2097152: raise ServiceError('Página descomprimida excede orçamento do cliente.')
                    return decode(content,values.loads,materialize_geometry)
            except HTTPError as error:
                if attempt==0 and self._retry(error): continue
                message,code,_=_refusal(error)
                raise ServiceError(message,error.code,None,code) from None
            except ServiceError:
                raise
            except (EOFError,gzip.BadGzipFile,zlib.error,ValueError) as error:
                raise ServiceError('Página recebida inválida ou incompleta: '+str(error)) from None
            except OSError as error:
                raise ServiceError('Servidor SAP inacessível: '+str(getattr(error,'reason',error))) from None


def query(**values):
    return '?'+urlencode(values)
