"""Telas do versionamento no QGIS: conflitos da finalização, desfazer, dividir,
fundir, histórico e as recusas por campo de um salvamento.

Portado do painel do plugin antigo (`dsg_versioning_qgis/plugin.py`): a tela de
resolução (itens da sessão, base/destino/origem/resultado com os rótulos do
modelo, resolver por um lado ou por edição, aceitar depreciação), o desfazer
salvamento, a divisão e a fusão com linhagem, o histórico com a linhagem, a
tabela de recusas por campo e o aviso de salvamento com "Recarregar camada".
O que NÃO veio: abrir repositório e clonar, preparar e aplicar integração
(o SAP faz isso no `finaliza`), releases, cobertura, clones, validação por
caixa e as prévias de estado no mapa. O lado do operador num merge do clone no
bloco: "meu" é a ORIGEM (`theirs`, o clone da atividade), "deles" é o DESTINO
(`ours`, o bloco, ou o lote na integração).

As chamadas são síncronas (cursor de espera): a tela é modal e o volume é o
de uma sessão de uma unidade de trabalho. Nenhuma chamada leva `actor`: o SAP
põe o `X-Dsg-Actor` com o login do token.

Sem import do pacote do plugin (só relativo): este diretório é copiado igual
para o SAP Gerente.
"""
import json
from uuid import uuid4

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QAbstractItemView,QApplication,QCheckBox,QComboBox,QDialog,QDialogButtonBox,
    QFormLayout,QHBoxLayout,QLabel,QLineEdit,QMessageBox,QPlainTextEdit,QPushButton,QTableWidget,QTableWidgetItem,QVBoxLayout)
from qgis.core import Qgis,QgsCoordinateTransform,QgsGeometry,QgsMessageLog,QgsProject,QgsVectorLayer,QgsWkbTypes

from . import model as model_rules
from . import provider as versioning
from . import values
from .client import ServiceError,query

LOG_TAG=versioning.LOG_TAG
# Lacuna do contrato (contrato-sap.md, seção 5): o repasse não abre `POST /jobs`
# ao operador e o ciclo do SAP não tem rota de atualização (pull) do clone da
# atividade a partir do bloco. O botão existe e fica escondido até o servidor
# oferecer a rota.
PULL_ROUTE_AVAILABLE=False

OPERATIONS={'insert':'Inclusão','update':'Alteração','delete':'Exclusão','deprecate':'Depreciação'}
LINEAGE_OPERATIONS={'split':'divisão','fuse':'fusão','deprecate':'depreciação','redistribute':'substituição','cancel':'cancelamento'}
CONFLICT_FIELDS={'$geometry':'Geometria','$feature':'Feição'}
CONFLICT_SIDES={'base':'da base','ours':'do destino','theirs':'da origem','result':'do resultado composto'}
GEOMETRY_REASONS={'self_intersection':'autointerseção','ring_self_intersection':'autointerseção de anel',
    'hole_outside_shell':'furo fora do contorno','nested_holes':'furos aninhados','disconnected_interior':'interior desconexo',
    'nested_shells':'contornos aninhados','duplicate_rings':'anéis duplicados','too_few_points':'pontos insuficientes',
    'invalid_coordinate':'coordenada inválida','ring_not_closed':'anel não fechado','repeated_point':'ponto repetido',
    'invalid_other':'outro motivo da GEOS'}
STATUSES={'merged':'composição automática','conflict':'conflito','resolved':'resolvido'}
# Lado do operador numa sessão de MERGE (`mode` push): a sessão mora no pai, e o
# clone da atividade (ou o bloco, na integração) é a origem, `theirs`.
MINE='theirs'; THEIRS='ours'


def sides(mode):
    """(meu, deles) de uma sessão pelo `mode` dela. No PULL a sessão mora no
    próprio clone do operador (destino, `ours`), e o pai é a origem; no merge é
    o contrário. Medido contra o serviço real no roteiro de ponta a ponta
    (controle_acervo, versionamento/docker/ponta_a_ponta): o pull do bloco no
    clone traz `ours` = o que o operador gravou."""
    return ('ours','theirs') if mode=='pull' else (MINE,THEIRS)


def json_text(value):
    return json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)


def operation_label(event):
    operation=event.get('operation')
    if operation in OPERATIONS: return OPERATIONS[operation]
    return 'Inclusão' if event.get('before') is None else 'Exclusão' if event.get('after') is None else 'Alteração'


def lineage_text(lineage):
    """Antecessoras e sucessoras de uma identidade."""
    def members(items):
        return ', '.join(m['id']+('' if m.get('alive') else ' (ausente)') for m in items) or 'nenhuma'
    lines=[]
    for event in lineage.get('predecessors') or []:
        lines.append('Antecessoras: '+members(event['predecessors'])+' · '+LINEAGE_OPERATIONS.get(event['operation'],event['operation'])+
                     ' por '+event['actor']+' em '+event['at']+' · motivo: '+event['reason'])
    for event in lineage.get('successors') or []:
        lines.append(('Sucessoras: '+members(event['successors']) if event['successors'] else 'Sem sucessoras')+' · '+
                     LINEAGE_OPERATIONS.get(event['operation'],event['operation'])+
                     ' por '+event['actor']+' em '+event['at']+' · motivo: '+event['reason'])
    return '\n'.join(lines) or 'Sem linhagem: a identidade não veio de divisão ou fusão nem foi depreciada.'


def conflict_text(conflict):
    """Um conflito como o integrador lê (geometria inválida chega como `<tipo>:<lado>:<código>:<texto GEOS>`)."""
    field=CONFLICT_FIELDS.get(conflict.get('field'),conflict.get('field'))
    reason=str(conflict.get('reason'))
    if reason.startswith('direction_reversed:'):
        side=CONFLICT_SIDES.get(reason.split(':')[1],'')
        return str(field)+': o sentido da linha '+side+' foi invertido. Trecho de drenagem e curva de nível exigem direção preservada. Decida pela resolução.'
    if reason.startswith('direction_unverifiable:'):
        return str(field)+': não foi possível comprovar que o sentido da linha foi preservado pelas correspondências de vértices. Decida pela resolução.'
    parts=reason.split(':',3)
    if len(parts)==4 and parts[0] in ('invalid_result_geometry','invalid_input_geometry'):
        kind,side,code,text=parts
        side=CONFLICT_SIDES.get(side,side); why=GEOMETRY_REASONS.get(code,code)+'; GEOS: '+text.strip()
        what=('o estado '+side+' que entraria no destino tem geometria inválida' if kind=='invalid_result_geometry'
              else 'a geometria '+side+' é inválida e não foi composta')
        return str(field)+': '+what+' ('+why+'). Decida pela resolução.'
    if reason=='core_error:vertex_budget_exceeded':
        return str(field)+': validade da geometria não verificada, acima do limite de vértices. Decida pela resolução.'
    if reason.startswith('core_error:'):
        return str(field)+': o núcleo de merge não compôs esta feição ('+reason[11:]+'). Decida pela resolução.'
    return str(field)+': '+reason


def connection_for(serviceBase):
    connection=versioning.connection_for(serviceBase)
    if connection is None:
        raise ValueError('Sem conexão com o versionamento do SAP.'+versioning.NOT_CONNECTED)
    return connection


def repo_layers(serviceBase,repo):
    """Camadas do provedor abertas no projeto para o repositório `repo`."""
    out=[]
    for layer in QgsProject.instance().mapLayers().values():
        if not isinstance(layer,QgsVectorLayer) or layer.providerType()!=versioning.PROVIDER_KEY: continue
        try: parts=versioning.parse_uri(layer.source())
        except ValueError: continue
        if parts['service']==serviceBase and parts['repo']==repo: out.append(layer)
    return out


def reload_layers(layers):
    for layer in layers:
        if layer.isValid(): layer.reload(); layer.updateExtents(); layer.triggerRepaint()


# Conflitos de uma sessão de merge ----------------------------------------------

class ConflictPayload:
    """O 409 do `finaliza`: `{sessao_id, conflitos}` no corpo ou em `dados` (envelope do SAP)."""
    def __init__(self,answer):
        answer=answer if isinstance(answer,dict) else {}
        inner=answer.get('dados') if isinstance(answer.get('dados'),dict) else {}
        def pick(*keys):
            for key in keys:
                for source in (inner,answer):
                    if source.get(key) not in (None,''): return source.get(key)
            return None
        self.session=pick('sessao_id','session_id')
        self.conflicts=pick('conflitos','conflicts') or []
        # O SAP diz em `repo_id` onde a sessão mora (controle_acervo,
        # server/src/versionamento/ciclo_atividade.js): o clone no pull, o pai
        # no merge. Sem ele, é o pai do repositório do pacote.
        self.repo=pick('repo_id_sessao','repositorio_sessao','repo_id')
        self.message=answer.get('message') or answer.get('error') or ''

    @property
    def valid(self): return bool(self.session)


def session_repository(client,packageRepo,payload=None):
    """Repositório onde vive a sessão do conflito: o `repo_id` do 409, que pode
    ser o próprio repositório do pacote (a sessão do pull mora no clone), ou,
    sem ele, o pai (`parent_id` do status do serviço), onde mora a do merge."""
    if payload is not None and payload.repo:
        return payload.repo
    status=client.request('/repos/'+packageRepo+'/status')
    parent=status.get('parent_id')
    if not parent:
        raise ValueError('O repositório '+packageRepo+' não tem pai: não há onde a sessão de merge viver.')
    return parent


class SessionResolver:
    """Lê os itens de uma sessão e grava as decisões (rotas de sessão do repasse)."""
    def __init__(self,client,repo,session):
        self.client=client; self.repo=repo; self.session=session
        self.attempts={}; self.rules_cache={}; self.model=None; self._sides=None

    def sides(self):
        """(meu, deles) desta sessão, pelo `mode` que o serviço diz (lido uma vez)."""
        if self._sides is None:
            self._sides=sides((self.describe() or {}).get('mode'))
        return self._sides

    def path(self,suffix=''):
        return '/repos/'+self.repo+'/sessions/'+self.session+suffix

    def describe(self):
        return self.client.request(self.path())

    def items(self,conflicts_only=True,cursor=None,limit=100):
        parameters={'limit':limit,'conflicts':'true' if conflicts_only else 'false'}
        if cursor: parameters.update(after_dataset=cursor['dataset'],after_id=cursor['id'])
        return self.client.request(self.path('/items')+query(**parameters))

    def rules(self,dataset):
        """Regras da classe no modelo do repositório da sessão, ou None."""
        if dataset in self.rules_cache: return self.rules_cache[dataset]
        found=None
        try:
            connection=versioning.connection_for(self.client.url)
            if connection is not None:
                specs=self.client.request('/repos/'+self.repo+'/datasets').get('datasets') or []
                spec=next((s for s in specs if s.get('name')==dataset),None)
                if spec is not None: found=connection.rules(self.repo,spec)
        except (ServiceError,ValueError,KeyError,TypeError) as error:
            QgsMessageLog.logMessage('Modelo do repositório da sessão não lido: '+str(error),LOG_TAG,Qgis.MessageLevel.Warning)
        self.rules_cache[dataset]=found
        return found

    def states(self,item):
        pending='a decidir' if item.get('status')=='conflict' else 'feição ausente'
        mine,theirs=self.sides()
        return model_rules.compare_lines(self.rules(item['dataset']),[
            ('base',item.get('base'),'feição ausente'),('deles',item.get(theirs),'feição ausente'),
            ('meu',item.get(mine),'feição ausente'),('resultado',item.get('result'),pending)])

    def resolve(self,item,choice,reason='',edited=None):
        """Decide um item: `choice` 'mine', 'theirs' ou 'edit' (com `edited`, o estado completo
        ou None para excluir). Um item contra depreciação só aceita a feição ausente."""
        if item.get('only_absent'):
            result=None; delete=True
        elif choice=='edit':
            result=edited; delete=edited is None
        else:
            mine,theirs=self.sides()
            state=item.get(mine if choice=='mine' else theirs)
            result=state; delete=state is None
        body=dict(dataset=item['dataset'],id=item['feature_id'],result=result,delete=bool(delete),reason=reason or '')
        content=json.dumps([self.repo,self.session,body],sort_keys=True,ensure_ascii=False)
        request_id=self.attempts.setdefault(content,str(uuid4()))
        # Estados lidos guardam cada número como o texto que o serviço mandou: volta literal.
        answer=values.loads(self.client.request_text(self.path('/resolve'),values.dumps(dict(body,request_id=request_id)),'POST'))
        self.attempts.pop(content,None)
        return answer


class ViolationsDialog(QDialog):
    """O que o modelo do repositório (ou a permissão da etapa) recusou num salvamento, por feição e campo."""
    def __init__(self,parent,title,violations):
        super().__init__(parent)
        self.setWindowTitle(title+' · recusas do salvamento'); self.setObjectName('dsgViolationsDialog'); self.resize(860,360)
        layout=QVBoxLayout(self)
        note=QLabel('Nada foi gravado. Corrija os campos abaixo e salve de novo; as edições continuam pendentes.')
        note.setWordWrap(True); layout.addWidget(note)
        table=QTableWidget(len(violations),5); table.setObjectName('dsgViolations')
        table.setHorizontalHeaderLabels(['Classe','Feição','Campo','Código','Motivo'])
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        for row,item in enumerate(violations):
            columns=[item.get('dataset'),item.get('id'),item.get('field') or '(identidade)',item.get('code'),item.get('detail')]
            for column,text in enumerate(columns): table.setItem(row,column,QTableWidgetItem(str(text)))
        table.resizeColumnsToContents(); table.horizontalHeader().setStretchLastSection(True); layout.addWidget(table)
        self.table=table
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject); buttons.accepted.connect(self.accept); layout.addWidget(buttons)


class Form(QDialog):
    def __init__(self,parent,title,fields):
        super().__init__(parent)
        self.setWindowTitle(title); self.setObjectName('dsgForm'); self.resize(540,350)
        layout=QVBoxLayout(self); form=QFormLayout(); layout.addLayout(form)
        self.controls={}
        for name,label,kind,value in fields:
            if kind in ('json','multiline'):
                widget=QPlainTextEdit(); widget.setPlainText(json_text(value) if kind=='json' else value); widget.setMinimumHeight(100)
            elif kind=='check':
                widget=QCheckBox(); widget.setChecked(bool(value))
            elif kind=='choice':
                widget=QComboBox()
                for key,text in value: widget.addItem(text,key)
            else:
                widget=QLineEdit(str(value))
            widget.setObjectName(name); widget.setAccessibleName(label)
            self.controls[name]=(widget,kind); form.addRow(label,widget)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); buttons.setObjectName('dialogButtons')
        layout.addWidget(buttons)

    def values(self):
        result={}
        for key,(widget,kind) in self.controls.items():
            if kind=='json': result[key]=json.loads(widget.toPlainText())
            elif kind=='multiline': result[key]=widget.toPlainText()
            elif kind=='check': result[key]=widget.isChecked()
            elif kind=='choice': result[key]=widget.currentData()
            else: result[key]=widget.text()
        return result


def _busy(callback):
    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    try: return callback()
    finally: QApplication.restoreOverrideCursor()


class ConflictDialog(QDialog):
    """Conflitos de uma sessão de merge (finalização da atividade ou integração).

    Aceita (`accept`) pelo botão "Finalizar de novo": quem abriu chama o
    `finaliza` outra vez. Fechar mantém a atividade em execução."""
    def __init__(self,parent,resolver,payload=None,retryLabel='Finalizar de novo'):
        super().__init__(parent)
        self.resolver=resolver; self.payload=payload; self.items=[]; self.cursor=None; self.next=None; self.pending=None
        self.setWindowTitle('Conflitos da integração · sessão '+resolver.session); self.setObjectName('dsgConflictDialog'); self.resize(900,600)
        layout=QVBoxLayout(self)
        intro=QLabel('O que você gravou na atividade ("meu") conflita com o que já foi integrado ("deles"). '
                     'Decida cada conflito e finalize de novo. Fechar esta tela mantém a atividade em execução.')
        intro.setWordWrap(True); layout.addWidget(intro)
        if payload is not None and payload.message:
            message=QLabel(payload.message); message.setWordWrap(True); message.setObjectName('conflictMessage'); layout.addWidget(message)
        self.only=QCheckBox('Só conflitos pendentes'); self.only.setChecked(True); self.only.setObjectName('conflictsOnly')
        self.only.toggled.connect(lambda _:self.guard(lambda:self.load(None))); layout.addWidget(self.only)
        self.table=QTableWidget(0,3); self.table.setObjectName('conflictItems')
        self.table.setHorizontalHeaderLabels(['Feição','Classe','Situação'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self.selected); layout.addWidget(self.table)
        self.details=QPlainTextEdit(); self.details.setReadOnly(True); self.details.setObjectName('conflictDetails'); layout.addWidget(self.details)
        self.summary=QLabel(); self.summary.setObjectName('conflictSummary'); layout.addWidget(self.summary)
        row=QHBoxLayout(); layout.addLayout(row)
        self.mine=self.button(row,'resolveMine','Manter o meu',lambda:self.decide('mine'))
        self.theirs=self.button(row,'resolveTheirs','Manter o deles',lambda:self.decide('theirs'))
        self.edit=self.button(row,'resolveEdit','Editar resultado',lambda:self.decide('edit'))
        self.more=self.button(row,'conflictNext','Próxima página',lambda:self.load(self.next)); self.more.setEnabled(False)
        row=QHBoxLayout(); layout.addLayout(row)
        self.notice=QLabel(); self.notice.setWordWrap(True); self.notice.setObjectName('conflictNotice'); row.addWidget(self.notice,1)
        self.retry=self.button(row,'conflictRetry',retryLabel,self.accept)
        close=self.button(row,'conflictClose','Fechar',self.reject)
        self.guard(lambda:self.load(None))

    def button(self,layout,name,text,callback):
        button=QPushButton(text); button.setObjectName(name); button.clicked.connect(lambda _=False:self.guard(callback))
        layout.addWidget(button); return button

    def guard(self,callback):
        try: return _busy(callback)
        except Exception as error:
            self.message(model_rules.refusal_text(error.violations,'\n') if getattr(error,'violations',None) else str(error),True)

    def message(self,text,error=False):
        self.notice.setText(text); self.notice.setStyleSheet('color: #a23434;' if error else 'color: #176e69;')

    def load(self,cursor=None):
        result=self.resolver.items(self.only.isChecked(),cursor)
        self.cursor=cursor; self.next=result.get('next'); self.items=result.get('items') or []
        self.table.blockSignals(True); self.table.setRowCount(len(self.items))
        for row,item in enumerate(self.items):
            status=STATUSES.get(item.get('status'),item.get('status'))+(': '+'; '.join(conflict_text(c) for c in item['conflicts']) if item.get('conflicts') else '')
            for column,text in enumerate((item['feature_id'],item['dataset'],status)): self.table.setItem(row,column,QTableWidgetItem(str(text)))
        self.table.blockSignals(False); self.details.clear()
        self.pending=int((result.get('counts') or {}).get('conflict',0))
        self.summary.setText(str(len(self.items))+' item(ns) na página; '+str(self.pending)+' conflito(s) pendente(s) no total.')
        self.more.setEnabled(self.next is not None)
        if self.pending==0: self.message('Nenhum conflito pendente: finalize de novo.')

    def current(self):
        row=self.table.currentRow()
        if row<0 or row>=len(self.items): raise ValueError('Selecione um item da sessão.')
        return self.items[row]

    def selected(self):
        if self.table.currentRow()<0 or not self.items: return
        item=self.current()
        reasons=''.join('Conflito · '+conflict_text(c)+'\n' for c in item.get('conflicts') or [])
        self.details.setPlainText(reasons+'\n'.join(self.resolver.states(item))+'\n\n'+json_text(item))

    def decide(self,choice,reason=None,edited=None,ask=True):
        item=self.current()
        if item.get('only_absent'):
            why=' '.join(c.get('message') or conflict_text(c) for c in item.get('conflicts') or [])
            if ask:
                dialog=Form(self,'Aceitar a depreciação: '+item['feature_id'],[('reason','Justificativa','multiline','')])
                note=QLabel(why+' A depreciação não se desfaz por resolução: o único resultado aceito é a feição ausente. '
                            'Refaça a alteração nas feições sucessoras.')
                note.setWordWrap(True); note.setTextFormat(Qt.TextFormat.PlainText); dialog.layout().insertWidget(0,note)
                if dialog.exec()!=QDialog.DialogCode.Accepted: return
                reason=dialog.values()['reason']
        elif choice=='edit' and ask:
            mine,theirs=self.resolver.sides()
            candidate=next((state for state in (item.get('result'),item.get(mine),item.get(theirs)) if state is not None),None)
            dialog=Form(self,'Resolver: '+item['feature_id'],[
                ('delete','Excluir a feição no resultado','check',False),
                ('result','Resultado completo','multiline',json_text(candidate)),('reason','Justificativa','multiline','')])
            remove,text=dialog.controls['delete'][0],dialog.controls['result'][0]
            remove.toggled.connect(lambda checked:text.setEnabled(not checked))
            states=QPlainTextEdit(); states.setReadOnly(True); states.setMaximumHeight(120); states.setPlainText('\n'.join(self.resolver.states(item)))
            dialog.layout().insertWidget(0,states); dialog.resize(640,520)
            if dialog.exec()!=QDialog.DialogCode.Accepted: return
            answer=dialog.values(); reason=answer['reason']
            if answer['delete']: edited=None
            else:
                edited=values.loads(answer['result'])
                if edited is None:
                    raise ValueError('Resultado nulo exclui a feição. Marque "Excluir a feição no resultado" para confirmar a exclusão.')
        self.resolver.resolve(item,choice,reason or '',edited)
        self.load(self.cursor)
        self.message('Decisão gravada para '+item['feature_id']+'.'+(' Nenhum conflito pendente: finalize de novo.' if not self.pending else ''))


# Ações do clone: desfazer, dividir, fundir, histórico ------------------------------

def undo_last_save(client,serviceBase,repo):
    """Desfaz o último salvamento do clone vivo e relê as camadas abertas dele."""
    layers=repo_layers(serviceBase,repo)
    if any(layer.isEditable() and layer.isModified() for layer in layers):
        raise ValueError('Salve ou descarte as edições pendentes das camadas antes de desfazer.')
    status=client.request('/repos/'+repo+'/status')
    result=client.request('/repos/'+repo+'/undo',{'expected_generation':status['generation']},'POST')
    reload_layers(layers)
    return result


def lineage_target(layer):
    """(partes do endereço, provedor, [(dsg_id, estado, geometria)]) das selecionadas na camada."""
    if layer is None or not isinstance(layer,QgsVectorLayer) or layer.providerType()!=versioning.PROVIDER_KEY or not layer.isValid():
        raise ValueError('Ative uma camada da atividade versionada e selecione nela as feições.')
    if layer.isEditable() and layer.isModified():
        raise ValueError('Salve ou descarte as edições pendentes da camada antes da operação: divisão e fusão são salvamentos próprios.')
    parts=versioning.parse_uri(layer.source()); source=layer.dataProvider()
    selected=[source.api_feature(feature.id())+(QgsGeometry(feature.geometry()),) for feature in layer.selectedFeatures()]
    return parts,source,sorted(selected,key=lambda item:item[0])


def lineage_request(client,layer,parts,operation,body,attempts):
    """Um salvamento de linhagem: geração atual, request_id estável para o mesmo conteúdo, releitura da camada."""
    repo=parts['repo']
    status=client.request('/repos/'+repo+'/status')
    payload=dict(body,expected_generation=status['generation'],dataset=parts['dataset'])
    content=json.dumps([repo,operation,payload],sort_keys=True,ensure_ascii=False)
    request_id=attempts.setdefault(content,str(uuid4()))
    answer=json.loads(client.request_text('/repos/'+repo+'/lineage/'+operation,values.dumps(dict(payload,request_id=request_id)),'POST'))
    attempts.pop(content,None)
    if layer.isValid(): layer.removeSelection(); layer.reload(); layer.updateExtents(); layer.triggerRepaint()
    return answer


def cut_line(layer):
    """WKT, no SRC de `layer`, da única linha selecionada em outra camada de linhas do projeto, ou ''."""
    project=QgsProject.instance()
    for other in project.mapLayers().values():
        if other is layer or not isinstance(other,QgsVectorLayer) or other.providerType()==versioning.PROVIDER_KEY: continue
        if other.geometryType()!=Qgis.GeometryType.Line or other.selectedFeatureCount()!=1: continue
        geometry=QgsGeometry(other.selectedFeatures()[0].geometry())
        if geometry.isNull(): continue
        geometry.transform(QgsCoordinateTransform(other.crs(),layer.crs(),project))
        if geometry.isMultipart(): geometry.convertToSingleType()
        return geometry.asWkt()
    return ''


def split(client,layer,cutWkt,reason,attempts):
    parts,source,selected=lineage_target(layer)
    if len(selected)!=1: raise ValueError('Selecione exatamente uma feição da camada ativa para dividir.')
    dsg_id,feature,geometry=selected[0]
    if layer.geometryType() not in (Qgis.GeometryType.Line,Qgis.GeometryType.Polygon):
        raise ValueError('A divisão por linha de corte vale para linhas e polígonos.')
    cut=QgsGeometry.fromWkt((cutWkt or '').strip())
    if cut.isNull() or QgsWkbTypes.geometryType(cut.wkbType())!=Qgis.GeometryType.Line:
        raise ValueError('Linha de corte inválida: informe uma LINESTRING em WKT.')
    if cut.isMultipart() and not cut.convertToSingleType():
        raise ValueError('Linha de corte inválida: informe uma única linha.')
    result,pieces,_=geometry.splitGeometry(cut.asPolyline(),False)
    if result!=Qgis.GeometryOperationResult.Success or not pieces:
        raise ValueError('A linha de corte não divide a feição selecionada.')
    label=source._label(dsg_id)
    members=[{'properties':feature['properties'],'geometry':source.geometry_to_api(piece,label)} for piece in [geometry]+list(pieces)]
    answer=lineage_request(client,layer,parts,'split',{'id':dsg_id,'parts':members,'reason':reason},attempts)
    return 'Feição '+dsg_id+' dividida em '+str(len(answer['parts']))+' partes ('+', '.join(answer['parts'])+'); a original foi depreciada.',answer


def fuse(client,layer,prevail,reason,attempts):
    parts,source,selected=lineage_target(layer)
    if len(selected)<2: raise ValueError('Selecione duas ou mais feições da camada ativa para fundir.')
    ids=[item[0] for item in selected]
    if prevail not in ids: raise ValueError('A feição cujos atributos prevalecem precisa estar entre as selecionadas.')
    union=QgsGeometry.unaryUnion([item[2] for item in selected])
    if layer.geometryType()==Qgis.GeometryType.Line: union=union.mergeLines()
    if union.isNull() or union.isEmpty(): raise ValueError('A união das geometrias selecionadas é vazia.')
    try:
        geometry=source.geometry_to_api(union,'Resultado da fusão')
    except ValueError as error:
        raise ValueError(str(error)+' As feições selecionadas precisam formar uma única geometria da classe.') from None
    properties=next(item[1]['properties'] for item in selected if item[0]==prevail)
    answer=lineage_request(client,layer,parts,'fuse',{'ids':ids,'result':{'properties':properties,'geometry':geometry},'reason':reason},attempts)
    return str(len(ids))+' feições fundidas em '+str(answer['result'])+'; as originais foram depreciadas.',answer


def history(client,repo,dataset,dsg_id,after=0):
    """(eventos, linhagem ou None) de uma identidade."""
    events=client.request('/repos/'+repo+'/history'+query(dataset=dataset,id=dsg_id,after=after,limit=100)).get('events') or []
    try: lineage=client.request('/repos/'+repo+'/lineage'+query(dataset=dataset,id=dsg_id))
    except ServiceError: lineage=None
    return events,lineage


class HistoryDialog(QDialog):
    def __init__(self,parent,title,events,lineage,rules=None):
        super().__init__(parent)
        self.events=events; self.rules=rules
        self.setWindowTitle('Histórico · '+title); self.setObjectName('dsgHistoryDialog'); self.resize(820,520)
        layout=QVBoxLayout(self)
        self.table=QTableWidget(len(events),3); self.table.setObjectName('historyEvents')
        self.table.setHorizontalHeaderLabels(['Operação','Autor','Quando'])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        for row,event in enumerate(events):
            for column,text in enumerate((operation_label(event),event.get('actor',''),event.get('occurred_at',''))):
                self.table.setItem(row,column,QTableWidgetItem(str(text)))
        self.table.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.table)
        self.details=QPlainTextEdit(); self.details.setReadOnly(True); layout.addWidget(self.details)
        self.table.itemSelectionChanged.connect(self.selected)
        self.lineage=QLabel(lineage_text(lineage) if lineage is not None else 'Linhagem não lida.')
        self.lineage.setWordWrap(True); self.lineage.setObjectName('historyLineage'); layout.addWidget(self.lineage)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def selected(self):
        row=self.table.currentRow()
        if 0<=row<len(self.events):
            event=self.events[row]
            self.details.setPlainText('\n'.join(model_rules.change_lines(self.rules,event.get('before'),event.get('after')))+'\n\n'+json_text(event))


class VersioningPanel(QDialog):
    """Ações do clone da atividade (ou do bloco, na integração)."""
    def __init__(self,parent,iface,serviceBase,versionamento,conflicts=None):
        super().__init__(parent)
        self.iface=iface; self.serviceBase=serviceBase; self.versionamento=dict(versionamento or {})
        self.repo=self.versionamento.get('repo_id'); self.conflicts=conflicts; self.attempts={}
        self.setWindowTitle('Versionamento da atividade'); self.setObjectName('dsgVersioningPanel'); self.resize(480,240)
        layout=QVBoxLayout(self)
        info=QLabel('Repositório '+str(self.repo)+' · papel '+str(self.versionamento.get('papel'))+
                    '. Desfazer, dividir e fundir são salvamentos no clone e valem enquanto ele vive.')
        info.setWordWrap(True); layout.addWidget(info)
        row=QHBoxLayout(); layout.addLayout(row)
        self.button(row,'versioningUndo','Desfazer último salvamento',self.undo)
        self.button(row,'versioningHistory','Histórico da feição',self.history)
        row=QHBoxLayout(); layout.addLayout(row)
        self.button(row,'versioningSplit','Dividir feição',self.split)
        self.button(row,'versioningFuse','Fundir feições',self.fuse)
        row=QHBoxLayout(); layout.addLayout(row)
        self.pull=self.button(row,'versioningPull','Atualizar com o bloco',self.update_from_parent)
        self.pull.setVisible(PULL_ROUTE_AVAILABLE)
        self.conflictsButton=self.button(row,'versioningConflicts','Conflitos pendentes',self.open_conflicts)
        self.conflictsButton.setVisible(callable(conflicts))
        self.notice=QLabel(); self.notice.setWordWrap(True); self.notice.setObjectName('versioningNotice'); layout.addWidget(self.notice)

    @property
    def client(self):
        return connection_for(self.serviceBase).client

    def button(self,layout,name,text,callback):
        button=QPushButton(text); button.setObjectName(name); button.clicked.connect(lambda _=False:self.guard(callback))
        layout.addWidget(button); return button

    def guard(self,callback):
        try: return _busy(callback)
        except Exception as error:
            self.message(model_rules.refusal_text(error.violations,'\n') if getattr(error,'violations',None) else str(error),True)

    def message(self,text,error=False):
        self.notice.setText(text); self.notice.setStyleSheet('color: #a23434;' if error else 'color: #176e69;')

    def active(self):
        return self.iface.activeLayer() if self.iface is not None else None

    def undo(self):
        result=undo_last_save(self.client,self.serviceBase,self.repo)
        cancelled=result.get('lineage_cancelled') or []
        self.message('Operação de linhagem cancelada: as originais voltaram e as partes foram removidas.' if cancelled else
                     'Salvamento desfeito: '+str(result.get('features',0))+' feição(ões) voltaram ao estado anterior.')

    def split(self,cutWkt=None,reason=None):
        layer=self.active()
        if cutWkt is None:
            dialog=Form(self,'Dividir feição',[('line','Linha de corte (WKT no SRC da camada)','multiline',cut_line(layer) if layer else ''),
                                               ('reason','Motivo da divisão (fica no histórico)','multiline','')])
            if dialog.exec()!=QDialog.DialogCode.Accepted: return
            answer=dialog.values(); cutWkt,reason=answer['line'],answer['reason']
        text,_=split(self.client,layer,cutWkt,reason or '',self.attempts)
        self.message(text+' Pode ser desfeita enquanto o clone vive.')

    def fuse(self,prevail=None,reason=None):
        layer=self.active()
        if prevail is None:
            _,_,selected=lineage_target(layer)
            ids=[item[0] for item in selected]
            dialog=Form(self,'Fundir feições',[('prevail','Atributos que prevalecem: os da feição','choice',[(key,key) for key in ids]),
                                               ('reason','Motivo da fusão (fica no histórico)','multiline','')])
            if dialog.exec()!=QDialog.DialogCode.Accepted: return
            answer=dialog.values(); prevail,reason=answer['prevail'],answer['reason']
        text,_=fuse(self.client,layer,prevail,reason or '',self.attempts)
        self.message(text+' Pode ser desfeita enquanto o clone vive.')

    def history(self,show=True):
        layer=self.active()
        parts,source,selected=lineage_target(layer)
        if len(selected)!=1: raise ValueError('Selecione uma feição da camada ativa para ver o histórico.')
        dsg_id=selected[0][0]
        events,lineage=history(self.client,parts['repo'],parts['dataset'],dsg_id)
        dialog=HistoryDialog(self,dsg_id,events,lineage,getattr(source,'rules',None))
        if show: dialog.exec()
        return dialog

    def update_from_parent(self):
        raise ValueError('O SAP ainda não oferece a atualização do clone a partir do bloco.')

    def open_conflicts(self):
        if callable(self.conflicts): self.conflicts()


# Avisos de salvamento do provedor ------------------------------------------------

class SaveReports:
    """Liga `provider.events.saveReport` à barra de mensagens do QGIS: recusa por
    campo abre a tabela de recusas; geração vencida oferece "Recarregar camada"."""
    def __init__(self,iface):
        self.iface=iface; self.last=None
        versioning.events.saveReport.connect(self.report)

    def disconnect(self):
        try: versioning.events.saveReport.disconnect(self.report)
        except TypeError: pass

    def layers(self,source):
        return [layer for layer in QgsProject.instance().mapLayers().values()
                if isinstance(layer,QgsVectorLayer) and layer.providerType()==versioning.PROVIDER_KEY and layer.source()==source]

    def violations(self,source):
        return next((items for items in (getattr(layer.dataProvider(),'last_violations',None) for layer in self.layers(source)) if items),[])

    def report(self,source,kind,message):
        layers=self.layers(source)
        title='Versionamento · '+(layers[0].name() if layers else 'camada')
        found=self.violations(source) if kind in ('refused','local') else []
        self.last=(source,kind,message,found)
        QgsMessageLog.logMessage(title+': '+message,LOG_TAG,Qgis.MessageLevel.Warning if kind!='saved' else Qgis.MessageLevel.Info)
        if self.iface is None: return
        try:
            bar=self.iface.messageBar(); widget=bar.createMessage(title,message)
        except Exception:
            return
        widget.setObjectName('dsgSaveReport')
        if kind=='stale' and layers:
            button=QPushButton('Recarregar camada'); button.setObjectName('dsgReloadLayer')
            button.clicked.connect(lambda _=False,source=source:reload_layers(self.layers(source)))
            widget.layout().addWidget(button)
        if found:
            button=QPushButton('Ver recusas por campo'); button.setObjectName('dsgShowViolations')
            button.clicked.connect(lambda _=False,found=found,title=title:ViolationsDialog(self.iface.mainWindow(),title,found).exec())
            widget.layout().addWidget(button)
        level=Qgis.MessageLevel.Success if kind=='saved' else Qgis.MessageLevel.Warning if kind=='stale' else Qgis.MessageLevel.Critical
        bar.pushWidget(widget,level,0)
