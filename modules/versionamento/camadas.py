"""Camadas do versionamento no projeto: reconhecer, abrir e ligar ao SAP.

Sem import do pacote do plugin (só relativo): este diretório é copiado igual
para o SAP Gerente (contrato-sap.md, seção 7).
"""
import json

from qgis.core import Qgis,QgsMessageLog,QgsProject,QgsVectorLayer

from . import provider as versioning
from .client import service_base

LOG_TAG=versioning.LOG_TAG
# Camada `ogr` aberta do GeoPackage de campo (campo.abrirCamadas): o par
# (schema, nome) do pacote, o dataset e o repositório, em JSON. Propriedade
# da camada, gravada no projeto: vale também quando o projeto é reaberto.
PROPRIEDADE_CAMPO='sap_versionamento/campo'


def dadosDeCampo(layer):
    """{schema, nome, dataset, repo_id} de uma camada do GeoPackage de campo, ou None."""
    try:
        if layer.providerType()!='ogr': return None
        value=layer.customProperty(PROPRIEDADE_CAMPO)
    except (AttributeError,RuntimeError):
        return None
    if not value: return None
    try:
        data=json.loads(value) if isinstance(value,str) else dict(value)
    except (ValueError,TypeError):
        return None
    return data if isinstance(data,dict) and data.get('nome') else None


def tabelaDaCamada(layer):
    """(schema, nome) da tabela de uma camada, ponto único de reconhecimento.

    PostGIS e o provedor `dsgversioning` respondem pelo `QgsDataSourceUri`: o
    endereço do versionamento leva `schema` e `table` da camada do pacote
    (provider.make_uri). Uma camada do versionamento com o endereço antigo
    (service=...&repo=...&dataset=...) responde ('', dataset), porque o
    dataset é nomeado pela tabela (contrato-sap.md, seção 6). A camada `ogr`
    do GeoPackage de campo (modo local do tipo 4, seção 9.4), cuja tabela no
    arquivo é a `f_<hash>` da classe, responde o par do `datasets` do pacote,
    guardado nela ao abrir. (None, None) quando a camada não tem provedor."""
    campo=dadosDeCampo(layer)
    if campo is not None:
        return campo.get('schema') or '',campo['nome']
    try:
        source=layer.dataProvider()
    except (AttributeError,RuntimeError):
        return None,None
    if source is None:
        return None,None
    if layer.providerType()==versioning.PROVIDER_KEY:
        try:
            parts=versioning.parse_uri(layer.source())
        except ValueError:
            return None,None
        return parts['schema'],parts['table']
    uri=source.uri()
    return uri.schema(),uri.table()


def ehVersionada(layer):
    """Camada do provedor `dsgversioning` (clone no servidor, pelo repasse do SAP)."""
    try:
        return layer.providerType()==versioning.PROVIDER_KEY
    except (AttributeError,RuntimeError):
        return False


def ehDeCampo(layer):
    """Camada `ogr` do GeoPackage de campo (modo local do tipo 4)."""
    return dadosDeCampo(layer) is not None


def ehDoVersionamento(layer):
    """Camada de um clone do versionamento, no servidor ou no GeoPackage de campo:
    o processing a acha pelo id, não pelo `uri()` remontado."""
    return ehVersionada(layer) or ehDeCampo(layer)


def conectar(sapServer,token,reauth=None):
    """Registra a conexão do repasse do SAP (o token é uma função lida a cada pedido)."""
    base=service_base(sapServer)
    versioning.register_connection(base,token,None,reauth)
    return base


def base(versionamento,sapServer):
    """Base do repasse: o `servico` do pacote (caminho no SAP) sobre o servidor."""
    route=str((versionamento or {}).get('servico') or '').rstrip('/')
    if route.startswith('http://') or route.startswith('https://'):
        return route
    if route:
        server=str(sapServer or '').rstrip('/')
        if server.endswith('/api'): server=server[:-4]
        return server+route
    return service_base(sapServer)


def abrirCamadas(serviceBase,versionamento,camadas,addToProject=True):
    """Abre pelo provedor as camadas do pacote (lista de {schema, nome}).

    Devolve (ids carregados, [(nome, motivo)] não carregadas). Camada sem
    dataset no pacote fica de fora com o motivo; nada vai para o banco."""
    datasets={(d.get('schema'),d.get('nome')):d.get('dataset') for d in (versionamento or {}).get('datasets') or []}
    byName={}
    for item in (versionamento or {}).get('datasets') or []:
        byName.setdefault(item.get('nome'),item.get('dataset'))
    loaded=[];missing=[]
    project=QgsProject.instance()
    for camada in camadas:
        schema=camada.get('schema') or ''; nome=camada.get('nome')
        dataset=datasets.get((schema,nome)) or byName.get(nome)
        if not dataset:
            missing.append((nome,'sem dataset no repositório da atividade'))
            continue
        uri=versioning.make_uri(serviceBase,versionamento['repo_id'],dataset,schema,nome)
        layer=QgsVectorLayer(uri,nome,versioning.PROVIDER_KEY)
        if not layer.isValid():
            reason=getattr(layer.dataProvider(),'open_error',None) or layer.error().summary() or 'camada inválida'
            missing.append((nome,reason))
            QgsMessageLog.logMessage('Camada '+str(nome)+' não abriu pelo versionamento: '+str(reason),LOG_TAG,Qgis.MessageLevel.Warning)
            continue
        versioning.attach_layer(layer)
        if addToProject:
            project.addMapLayer(layer)
        loaded.append(layer.id())
    return loaded,missing


def aplicarFiltro(layer,expression):
    """Filtro de camada por expressão (o `dsgversioning` avalia a expressão
    QGIS sobre o cache; o `ogr` do GeoPackage de campo, em SQL); False, com
    a lacuna registrada no log, quando o provedor recusa o filtro."""
    if not expression:
        return True
    if layer.setSubsetString(expression):
        return True
    QgsMessageLog.logMessage('Lacuna: o provedor '+layer.providerType()+' não aceita filtro de camada; a camada '+layer.name()+
                             ' abre sem o filtro '+expression+'.',LOG_TAG,Qgis.MessageLevel.Warning)
    return False
