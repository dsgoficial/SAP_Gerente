"""Modo local do tipo 4: o clone da atividade em GeoPackage, aberto direto pelo
QGIS (provedor `ogr`), sem rede (contrato-sap.md, seção 9.4).

O SAP Gerente baixa o arquivo do clone (seção 9.1) ao lado do pacote local e
põe em `versionamento` o nome dele (`arquivo`, sem caminho) e o `sha256`. O
arquivo é um repositório do serviço: a edição direta é capturada pelos
gatilhos do próprio GeoPackage e registrada no servidor depois, no `prepare`,
com a cobrança do modelo e da permissão da etapa. O que a edição direta exige
(`versionamento/backend/storage-gpkg`, `ddl.rs` e `class.rs`):

- a classe mora na tabela `f_` + 20 dígitos hexadecimais do SHA-256 do nome
  (`dsg_classes.name` -> `table_name`); a camada abre por ela;
- `dsg_id` é NOT NULL, único e UUID canônico (minúsculo, com hífens), sem
  valor padrão no arquivo: a feição nova recebe a identidade aqui; um
  gatilho recusa trocar a de uma feição existente;
- os gatilhos da R*Tree chamam as funções `ST_` que o GDAL registra, então
  só o QGIS (ou o GDAL) grava geometria no arquivo;
- `dsg_meta.permissions` é a permissão da etapa por classe, cobrada no
  `prepare`: o plugin a aplica na edição, para a recusa não chegar só na
  volta do arquivo.

Abrir o arquivo no QGIS já muda os bytes dele, mesmo sem edição: o SHA-256 do
pacote só confere antes da primeira abertura. A conferência fica registrada num
arquivo ao lado (`<arquivo>.sap-conferido.json`), e nas aberturas seguintes vale
a identidade do repositório (`dsg_meta.repo_id`).

Sem import do pacote do plugin (só relativo): este diretório é copiado igual
para o SAP Gerente (contrato-sap.md, seção 7).
"""
import copy
import hashlib
import json
import os
import re
import sqlite3
import time
import uuid
from pathlib import Path

from qgis.PyQt.QtCore import QObject,QTimer
from qgis.core import (Qgis,QgsAction,QgsDefaultValue,QgsEditorWidgetSetup,QgsExpression,QgsFeatureRequest,QgsMessageLog,
    QgsProject,QgsVectorLayer)

from . import model as model_rules
from . import values
from .camadas import PROPRIEDADE_CAMPO,dadosDeCampo,tabelaDaCamada
from .provider import LOG_TAG,widget_setup

FAMILIA='dsg-versioning'
ID_FIELD='dsg_id'
# Identidade da feição nova, sem aspas simples: o menu de aquisição do DsgTools
# guarda e restaura o valor padrão entre aspas, e uma expressão sem aspas
# continua um texto válido (a identidade inválida é trocada antes de gravar).
ID_DEFAULT='lower(substr(uuid(),2,36))'
MARCADOR='.sap-conferido.json'
_HEX64=re.compile('[0-9a-f]{64}')


class CampoError(ValueError):
    """O GeoPackage de campo não pode ser usado: a mensagem diz por quê e o que fazer."""


def nomeDoArquivo(versionamento):
    """Nome do GeoPackage de campo no pacote (`versionamento.arquivo`), sem caminho."""
    nome=str((versionamento or {}).get('arquivo') or '').strip()
    if not nome:
        raise CampoError('O pacote local não diz o nome do GeoPackage de campo (versionamento.arquivo). '
                         'Gere o pacote de novo pelo SAP Gerente.')
    if nome in ('.','..') or os.path.basename(nome)!=nome or '/' in nome or '\\' in nome:
        raise CampoError('O nome do GeoPackage de campo no pacote tem caminho ('+nome+'); o pacote só pode trazer o nome do arquivo.')
    return nome


def localizarArquivo(nome,pastas):
    """Primeiro `<pasta>/<nome>` que existe, ou None."""
    for pasta in pastas:
        if not pasta: continue
        caminho=os.path.join(str(pasta),nome)
        if os.path.isfile(caminho): return caminho
    return None


def sha256(caminho,bloco=1<<20):
    digest=hashlib.sha256()
    with open(caminho,'rb') as arquivo:
        for parte in iter(lambda:arquivo.read(bloco),b''):
            digest.update(parte)
    return digest.hexdigest()


def _conectar(caminho):
    """Leitura sem escrita no arquivo; `immutable` quando o SQLite não abre o WAL só para leitura."""
    uri=Path(caminho).resolve().as_uri()
    try:
        db=sqlite3.connect(uri+'?mode=ro',uri=True,timeout=5)
        db.execute('SELECT 1 FROM sqlite_master LIMIT 1')
        return db
    except sqlite3.Error:
        return sqlite3.connect(uri+'?immutable=1',uri=True)


def _modeloDaApi(texto):
    """O documento `dsg-model/1` gravado em `dsg_model` na forma da rota `GET /model`
    do serviço (domínios e classes por nome), que `model.ClassRules` lê."""
    documento=json.loads(texto)
    dominios={d['name']:[{'code':v['code'],'label':v.get('label')} for v in d.get('values') or []]
              for d in documento.get('domains') or []}
    classes={}
    for classe in documento.get('classes') or []:
        campos={f['name']:{k:v for k,v in f.items() if k!='name'} for f in classe.get('fields') or []}
        classes[classe['name']]={'identity':classe.get('identity'),'fields':campos}
    return {'digest':hashlib.sha256(texto.encode('utf-8')).hexdigest(),'name':documento.get('name'),
            'version':documento.get('version'),'domains':dominios,'classes':classes}


def lerRepositorio(caminho):
    """`{meta, classes: {nome: {table, spec}}, modelo}` do GeoPackage do clone."""
    try:
        db=_conectar(caminho)
    except sqlite3.Error as error:
        raise CampoError('O GeoPackage de campo '+os.path.basename(caminho)+' não abre: '+str(error)) from None
    try:
        try:
            meta=dict(db.execute('SELECT key,value FROM dsg_meta').fetchall())
            linhas=db.execute('SELECT name,table_name,spec FROM dsg_classes').fetchall()
        except sqlite3.Error:
            raise CampoError('O arquivo '+os.path.basename(caminho)+' não é um repositório do versionamento '
                             '(sem dsg_meta ou dsg_classes).') from None
        classes={}
        for nome,tabela,spec in linhas:
            try: spec=json.loads(spec)
            except ValueError: spec={'fields':[]}
            classes[nome]={'table':tabela,'spec':spec}
        modelo=None
        try:
            linha=db.execute('SELECT document FROM dsg_model WHERE k = 1').fetchone()
        except sqlite3.Error:
            linha=None
        if linha:
            try: modelo=_modeloDaApi(linha[0])
            except (ValueError,KeyError,TypeError) as error:
                QgsMessageLog.logMessage('Modelo do GeoPackage de campo não lido: '+str(error),LOG_TAG,Qgis.MessageLevel.Warning)
        return {'meta':meta,'classes':classes,'modelo':modelo}
    finally:
        db.close()


def _marcador(caminho):
    return str(caminho)+MARCADOR


def _lerMarcador(caminho):
    try:
        with open(_marcador(caminho),encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except (OSError,ValueError):
        return None


def conferirArquivo(caminho,versionamento):
    """Confere o GeoPackage de campo contra o pacote; CampoError quando não confere.

    Antes da primeira abertura, o SHA-256 do arquivo tem de ser o do pacote; a
    conferência fica registrada ao lado do arquivo. Depois dela (o QGIS muda
    os bytes ao abrir e ao gravar), vale a identidade do repositório. Em
    qualquer caso o arquivo é um repositório do versionamento, do `repo_id`
    do pacote, e o clone não está encerrado. Devolve `{estado, repositorio}`,
    com `estado` 'conferido' (SHA-256 igual ao do pacote) ou 'em edição'."""
    versionamento=versionamento or {}
    nome=os.path.basename(str(caminho))
    esperado=str(versionamento.get('sha256') or '').strip().lower()
    if not _HEX64.fullmatch(esperado):
        raise CampoError('O pacote local não traz o SHA-256 do GeoPackage de campo (versionamento.sha256). '
                         'Gere o pacote de novo pelo SAP Gerente.')
    repo=str(versionamento.get('repo_id') or '')
    if not os.path.isfile(caminho):
        raise CampoError('GeoPackage de campo não encontrado: '+nome+'.')
    marca=_lerMarcador(caminho)
    if marca and marca.get('repo_id')==repo and marca.get('sha256')==esperado:
        estado='em edição'
    else:
        atual=sha256(caminho)
        if atual!=esperado:
            raise CampoError('O GeoPackage de campo '+nome+' não confere com o pacote local: SHA-256 '+atual+
                             ', e o pacote espera '+esperado+'. Copie de novo o arquivo que o SAP Gerente baixou com este pacote.')
        estado='conferido'
    repositorio=lerRepositorio(caminho)
    meta=repositorio['meta']
    if meta.get('family')!=FAMILIA:
        raise CampoError('O arquivo '+nome+' não é um repositório do versionamento.')
    if meta.get('repo_id')!=repo:
        raise CampoError('O GeoPackage de campo '+nome+' é do repositório '+str(meta.get('repo_id'))+
                         ', e o pacote local é do repositório '+repo+'.')
    if 'closure' in meta:
        raise CampoError('O clone do GeoPackage de campo '+nome+' está encerrado (integrado ou descartado) e não aceita edição.')
    if estado=='conferido':
        try:
            with open(_marcador(caminho),'w',encoding='utf-8') as arquivo:
                json.dump({'repo_id':repo,'sha256':esperado,'arquivo':nome,
                           'conferido_em':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},arquivo,ensure_ascii=False)
        except OSError as error:
            raise CampoError('A pasta do GeoPackage de campo não aceita gravação ('+str(error)+'): o QGIS não poderá editar o arquivo.') from None
    return {'estado':estado,'repositorio':repositorio}


def permissoes(repositorio):
    """`dsg_meta.permissions` do clone ({classe: {insert, delete, geometry, fields}}), ou None (tudo editável)."""
    texto=(repositorio or {}).get('meta',{}).get('permissions')
    if not texto: return None
    try:
        valor=json.loads(texto)
    except ValueError:
        return None
    return valor if isinstance(valor,dict) else None


def _uri(caminho,tabela):
    return str(caminho)+'|layername='+tabela


def abrirCamadas(caminho,versionamento,camadas,repositorio=None,addToProject=True):
    """Abre do GeoPackage de campo, pelo `ogr`, as camadas do pacote (lista de {schema, nome}).

    Devolve (ids carregados, [(nome, motivo)] não carregadas). Cada camada leva
    o par (schema, nome) do pacote numa propriedade (tabelaDaCamada), a
    identidade nova das feições, os domínios e os valores padrão do modelo do
    clone no formulário e a permissão da etapa."""
    repositorio=repositorio or lerRepositorio(caminho)
    datasets={(d.get('schema'),d.get('nome')):d.get('dataset') for d in (versionamento or {}).get('datasets') or []}
    porNome={}
    for item in (versionamento or {}).get('datasets') or []:
        porNome.setdefault(item.get('nome'),item.get('dataset'))
    carregadas=[];faltando=[]
    projeto=QgsProject.instance()
    for camada in camadas:
        schema=camada.get('schema') or ''; nome=camada.get('nome')
        dataset=datasets.get((schema,nome)) or porNome.get(nome)
        if not dataset:
            faltando.append((nome,'sem dataset no repositório da atividade')); continue
        classe=repositorio['classes'].get(dataset)
        if classe is None:
            faltando.append((nome,'a classe '+dataset+' não está no GeoPackage de campo')); continue
        layer=QgsVectorLayer(_uri(caminho,classe['table']),nome,'ogr')
        if not layer.isValid():
            motivo=layer.error().summary() or 'camada inválida'
            faltando.append((nome,motivo))
            QgsMessageLog.logMessage('Camada '+str(nome)+' não abriu do GeoPackage de campo: '+motivo,LOG_TAG,Qgis.MessageLevel.Warning)
            continue
        layer.setCustomProperty(PROPRIEDADE_CAMPO,json.dumps({'schema':schema,'nome':nome,'dataset':dataset,
                                                               'repo_id':(versionamento or {}).get('repo_id')},ensure_ascii=False))
        _configurar(layer,dataset,classe,repositorio)
        ligarCamada(layer,repositorio)
        if addToProject: projeto.addMapLayer(layer)
        carregadas.append(layer.id())
    return carregadas,faltando


def padraoDoModelo(spec,rules):
    """Expressão do valor padrão LITERAL do modelo do clone para o campo, ou None.

    Como no provedor remoto (`DsgVersioningProvider.defaultValue`): o
    repositório não aplica valor padrão, e a feição nova sai do formulário com
    o literal do modelo; o padrão por expressão do modelo é ignorado."""
    found,value=rules.default(spec['name'])
    if not found or value is None: return None
    try:
        valor=values.from_model(spec,value)
    except (ValueError,TypeError,KeyError):
        QgsMessageLog.logMessage('Valor padrão do modelo ignorado em '+str(spec.get('name'))+': '+json.dumps(value,ensure_ascii=False),
                                 LOG_TAG,Qgis.MessageLevel.Warning)
        return None
    if isinstance(valor,(bool,int,float,str)): return QgsExpression.quotedValue(valor)
    return QgsExpression.quotedString(str(value))


def _configurar(layer,dataset,classe,repositorio):
    """Identidade nova, campos de controle só leitura, domínios e valores padrão do modelo no formulário."""
    fields=layer.fields()
    index=fields.indexOf(ID_FIELD)
    config=layer.editFormConfig()
    if index>=0:
        layer.setDefaultValueDefinition(index,QgsDefaultValue(ID_DEFAULT))
        config.setReadOnly(index,True)
    fid=fields.indexOf('fid')
    if fid>=0: config.setReadOnly(fid,True)
    layer.setEditFormConfig(config)
    modelo=repositorio.get('modelo')
    if modelo is None: return
    specs=[f for f in (classe.get('spec') or {}).get('fields') or [] if not str(f.get('kind') or '').startswith('geometry')]
    required=[f['name'] for f in specs if f.get('nullable') is False]
    rules=model_rules.class_rules(modelo,{dataset:required},{'name':dataset,'fields':specs})
    for spec in specs:
        position=fields.indexOf(spec['name'])
        if position<0: continue
        setup=widget_setup(spec,rules)
        if setup is not None: layer.setEditorWidgetSetup(position,setup)
        padrao=padraoDoModelo(spec,rules)
        if padrao is not None: layer.setDefaultValueDefinition(position,QgsDefaultValue(padrao))


def ligarCamada(layer,repositorio=None):
    """Liga à camada de campo a identidade nova e a permissão da etapa. Idempotente;
    chamada também quando um projeto salvo é reaberto (versionamento._attach)."""
    dados=dadosDeCampo(layer)
    if dados is None or layer.providerType()!='ogr' or layer.property('sap_versionamento_campo_ligada'):
        return None
    if repositorio is None:
        try:
            repositorio=lerRepositorio(layer.source().split('|')[0])
        except CampoError as error:
            QgsMessageLog.logMessage(str(error),LOG_TAG,Qgis.MessageLevel.Warning)
            repositorio={'meta':{}}
    todas=permissoes(repositorio)
    permissao=None if todas is None else todas.get(dados.get('dataset'),False)
    if permissao is False:
        # Classe fora da permissão da etapa: somente leitura (contrato-sap.md, seção 3).
        layer.setReadOnly(True)
    elif permissao is not None and permissao.get('fields') is not None:
        livres=set(permissao['fields'])|{ID_FIELD,'fid'}
        config=layer.editFormConfig()
        for index,field in enumerate(layer.fields()):
            if field.name() not in livres: config.setReadOnly(index,True)
        layer.setEditFormConfig(config)
    guarda=GuardaDeCampo(layer,None if permissao is False else permissao)
    layer.setProperty('sap_versionamento_campo_ligada',True)
    return guarda


class GuardaDeCampo(QObject):
    """Edição da camada de campo: identidade de feição nova antes de gravar e
    permissão da etapa na hora.

    A gravação no GeoPackage não passa pelo serviço: uma edição fora da
    permissão (inserir, excluir, mexer na geometria ou num campo que a etapa
    não libera) só seria recusada no `prepare`, depois da volta do arquivo.
    A guarda desfaz a edição assim que ela entra no buffer e avisa; o que
    escapar dela (camada ligada depois da edição) é avisado ao gravar."""

    def __init__(self,layer,permissao):
        super().__init__(layer)
        self.layer=layer
        self.permissao=permissao
        self.mensagens=[]
        self._indice=layer.undoStack().index()
        layer.beforeCommitChanges.connect(self.antesDeGravar)
        restrita=permissao is not None and (not all(permissao.get(k) for k in ('insert','delete','geometry'))
                                            or permissao.get('fields') is not None)
        if restrita:
            layer.undoStack().indexChanged.connect(self._mudou)

    def _nome(self):
        return tabelaDaCamada(self.layer)[1] or self.layer.name()

    def violacoes(self):
        """O que o buffer de edição tem fora da permissão da etapa."""
        permissao=self.permissao
        buffer=self.layer.editBuffer()
        if permissao is None or buffer is None: return []
        found=[]
        if not permissao.get('insert') and buffer.addedFeatures():
            found.append('inserir feição')
        if not permissao.get('delete') and any(fid>=0 for fid in buffer.deletedFeatureIds()):
            found.append('excluir feição')
        if not permissao.get('geometry') and any(fid>=0 for fid in buffer.changedGeometries()):
            found.append('alterar geometria')
        livres=permissao.get('fields')
        if livres is not None:
            livres=set(livres)|{ID_FIELD,'fid'}
            fields=self.layer.fields()
            nomes=set()
            for fid,changes in buffer.changedAttributeValues().items():
                if fid<0: continue
                for index in changes:
                    name=fields.at(int(index)).name()
                    if name not in livres: nomes.add(name)
            found+=['alterar o campo '+name for name in sorted(nomes)]
        return found

    def _mudou(self,index):
        anterior=self._indice; self._indice=index
        if index<=anterior: return
        found=self.violacoes()
        if found: QTimer.singleShot(0,lambda:self._desfazer(index,found))

    def _desfazer(self,index,found):
        stack=self.layer.undoStack()
        if stack.index()!=index: return
        stack.undo()
        self._avisar('Edição não permitida nesta etapa em '+self._nome()+' ('+', '.join(found)+'): a alteração foi desfeita. '
                     'O servidor recusaria o GeoPackage de campo na volta (permissão da atividade).',Qgis.MessageLevel.Warning)

    def antesDeGravar(self,_stopEditing=False):
        """Toda feição nova sai com identidade UUID canônica e única; avisa o que fura a permissão."""
        self._identidades()
        found=self.violacoes()
        if found:
            self._avisar('Gravação em '+self._nome()+' com edição fora da permissão da etapa ('+', '.join(found)+'): '
                         'o servidor vai recusar o GeoPackage de campo na volta. Desfaça essas alterações.',Qgis.MessageLevel.Critical)

    def _identidades(self):
        layer=self.layer; buffer=layer.editBuffer()
        index=layer.fields().indexOf(ID_FIELD)
        if buffer is None or index<0: return
        added=buffer.addedFeatures()
        if not added: return
        valores={fid:feature.attribute(index) for fid,feature in added.items()}
        candidatos=sorted({str(v) for v in valores.values() if model_rules.is_canonical_uuid(str(v))})
        existentes=set()
        for start in range(0,len(candidatos),200):
            parte=candidatos[start:start+200]
            request=QgsFeatureRequest().setFilterExpression('"{0}" IN ({1})'.format(ID_FIELD,','.join(QgsExpression.quotedString(v) for v in parte)))
            request.setFlags(Qgis.FeatureRequestFlag.NoGeometry).setSubsetOfAttributes([index])
            for feature in layer.dataProvider().getFeatures(request):
                existentes.add(str(feature.attribute(index)))
        vistos=set()
        for fid in sorted(valores):
            valor=str(valores[fid]) if valores[fid] is not None else ''
            if not model_rules.is_canonical_uuid(valor) or valor in vistos or valor in existentes:
                valor=str(uuid.uuid4())
                layer.changeAttributeValue(fid,index,valor)
            vistos.add(valor)

    def _avisar(self,texto,nivel):
        self.mensagens.append(texto)
        QgsMessageLog.logMessage(texto,LOG_TAG,nivel)
        try:
            from qgis.utils import iface
            iface.messageBar().pushMessage('SAP Operador',texto,level=nivel,duration=10)
        except Exception:
            pass


# Configuração da atividade que o DsgTools casa por `uri().table()` --------------
# Os algoritmos de apelidos e ações do DsgTools acham a camada pela tabela do
# endereço, que a camada `ogr` do GeoPackage de campo não tem (é o caminho do
# arquivo). Aqui vale a mesma semântica, com a camada achada por tabelaDaCamada.

def aplicarApelidos(layers,definicao):
    """Como `dsgtools:assignaliasestolayersalgorithm` (`camadaNome`, `camadaApelido`, `atributosApelido`)."""
    if not definicao: return []
    dados=json.loads(definicao) if isinstance(definicao,str) else definicao
    nomes=[item['camadaNome'] for item in dados]
    feitas=[]
    for layer in layers:
        nome=tabelaDaCamada(layer)[1]
        if nome not in nomes: continue
        item=dados[nomes.index(nome)]
        if item.get('camadaApelido'): layer.setName(item['camadaApelido'])
        for atributo in item.get('atributosApelido') or []:
            index=layer.fields().indexOf(atributo['nome'])
            if not index>0: continue
            anterior=QgsEditorWidgetSetup(layer.editorWidgetSetup(index)) if layer.editorWidgetSetup(index).config() else None
            layer.setFieldAlias(index,atributo['alias'])
            if anterior is not None: layer.setEditorWidgetSetup(index,anterior)
        feitas.append(layer.id())
    return feitas


def aplicarAcoes(layers,acoes):
    """Como `dsgtools:assignactionstolayersalgorithm` (`camadaNome`, `tipo`, `descricao`, `documentacao`)."""
    tipos={'Generic':QgsAction.ActionType.Generic,'GenericPython':QgsAction.ActionType.GenericPython,
           'Mac':QgsAction.ActionType.Mac,'Windows':QgsAction.ActionType.Windows,'Unix':QgsAction.ActionType.Unix,
           'OpenUrl':QgsAction.ActionType.OpenUrl}
    acoes=list(acoes or [])
    nomes=[item['camadaNome'] for item in acoes]
    feitas=[]
    for layer in layers:
        nome=tabelaDaCamada(layer)[1]
        if nome not in nomes: continue
        item=acoes[nomes.index(nome)]
        if not item.get('documentacao'): continue
        acao=QgsAction(tipos[item['tipo']],item['descricao'],"[%'{}'%]".format(item['documentacao']))
        acao.setActionScopes({'Feature','Canvas'})
        layer.actions().addAction(acao)
        feitas.append(layer.id())
    return feitas


def nomeNosMenus(layer):
    """Nome com que o menu de aquisição do DsgTools acha uma camada `ogr`
    (`Modules/qgis/controllers/qgisCtrl.py`, getVectorLayersByName): a tabela do
    endereço do arquivo, que no GeoPackage de campo é a `f_<hash>` da classe."""
    nome=layer.dataProvider().uri().uri().split('|')[-1].split('=')[-1][1:-1]
    return nome or layer.name()


def traduzirMenus(menus,layers):
    """Os menus da atividade com o `buttonLayer` de cada camada de campo trocado
    pelo nome com que o DsgTools a acha (nomeNosMenus); o resto fica igual."""
    trocas={}
    for layer in layers:
        if dadosDeCampo(layer) is None: continue
        trocas[tabelaDaCamada(layer)[1]]=nomeNosMenus(layer)
    def trocar(valor):
        if isinstance(valor,dict):
            return {k:(trocas.get(v,v) if k=='buttonLayer' and isinstance(v,str) else trocar(v)) for k,v in valor.items()}
        if isinstance(valor,list): return [trocar(v) for v in valor]
        return valor
    return [trocar(copy.deepcopy(menu)) for menu in menus or []]
