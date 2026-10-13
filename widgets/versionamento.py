# -*- coding: utf-8 -*-
# Ações do versionamento no SAP Gerente (contrato do versionamento no SAP 3.0,
# seção 5): versionar o lote, versionar o bloco e acompanhar os repositórios.
#
# O clone é tarefa longa no serviço. O SAP responde 202 com o `job_id`, e o
# progresso é lido por `GET /api/versionamento/servico/jobs/:id` numa QgsTask,
# fora da linha da interface: a tarefa só lê HTTP e emite sinais; quem mexe nos
# widgets é a linha principal, nos slots.
#
# A camada versionada (provedor `dsgversioning`) NÃO é aberta aqui. Quando o
# Gerente precisar abrir uma, o provedor vem de `modules/versionamento/`, copiado
# do SAP Operador (contrato, seção 7). PONTO MARCADO: abrir camada versionada.

import time

from qgis.PyQt import QtCore, QtWidgets
from qgis.core import QgsApplication, QgsTask

from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory
from SAP_Gerente.modules.sap.api.contrato import (
    JOB_TERMINAIS, ehBaseVersionada, jobIdDaResposta, resumoJob, rotuloDadoProducao
)

try:
    from qgis.PyQt import sip
except ImportError:
    import sip


class VersionamentoJobTask(QgsTask):
    # Lê a tarefa do serviço até ela terminar. `run` roda em outra linha: nada
    # de widget aqui, só o sinal `atualizado` com o JSON da tarefa.

    atualizado = QtCore.pyqtSignal(dict)

    INTERVALO = 2.0
    TETO_FALHAS = 5

    def __init__(self, sap, jobId):
        super(VersionamentoJobTask, self).__init__(
            'Versionamento: tarefa {0}'.format(jobId),
            QgsTask.Flag.CanCancel
        )
        self.sap = sap
        self.jobId = jobId
        self.job = None
        self.erro = None

    def run(self):
        falhas = 0
        while not self.isCanceled():
            try:
                job = self.sap.getVersionamentoJob(self.jobId)
                falhas = 0
            except Exception as e:
                # Uma leitura que falha não encerra o acompanhamento; várias
                # seguidas, sim, com o motivo.
                falhas += 1
                if falhas >= self.TETO_FALHAS:
                    self.erro = str(e)
                    return False
                time.sleep(self.INTERVALO)
                continue
            if isinstance(job, dict):
                self.job = job
                self.atualizado.emit(job)
                if job.get('state') in JOB_TERMINAIS:
                    return job.get('state') == 'succeeded'
            time.sleep(self.INTERVALO)
        return False


class AcompanhadorJob(QtCore.QObject):
    # Liga uma QgsTask de acompanhamento a um rótulo e a uma barra. A barra fica
    # indeterminada: o `completed` do serviço é contagem, não porcentagem.

    terminou = QtCore.pyqtSignal(dict)

    def __init__(self, sap, rotulo, barra, parent=None):
        super(AcompanhadorJob, self).__init__(parent)
        self.sap = sap
        self.rotulo = rotulo
        self.barra = barra
        self.task = None

    def emAndamento(self):
        return self.task is not None

    def iniciar(self, jobId):
        self.cancelar()
        task = VersionamentoJobTask(self.sap, jobId)
        self.task = task
        task.atualizado.connect(lambda job, task=task: self._atualizar(task, job))
        task.taskCompleted.connect(lambda task=task: self._fim(task))
        task.taskTerminated.connect(lambda task=task: self._fim(task))
        self.barra.setRange(0, 0)
        self.barra.setVisible(True)
        self.rotulo.setText('Tarefa {0}: aguardando o serviço...'.format(jobId))
        QgsApplication.taskManager().addTask(self.task)

    def cancelar(self):
        if self.task is not None:
            try:
                self.task.cancel()
            except RuntimeError:
                pass
        self.task = None

    def _vivo(self):
        return not ( sip.isdeleted(self.rotulo) or sip.isdeleted(self.barra) )

    def _atualizar(self, task, job):
        # Sinal de uma tarefa já trocada por outra (ou cancelada) é ignorado.
        if task is self.task and self._vivo():
            self.rotulo.setText('Tarefa {0}: {1}'.format(job.get('id', ''), resumoJob(job)))

    def _fim(self, task):
        if task is not self.task:
            return
        self.task = None
        if not self._vivo():
            return
        self.barra.setRange(0, 1)
        self.barra.setValue(1)
        job = task.job or {}
        if task.erro:
            self.rotulo.setText('Tarefa {0}: sem resposta do serviço ({1})'.format(task.jobId, task.erro))
        elif job:
            self.rotulo.setText('Tarefa {0}: {1}'.format(task.jobId, resumoJob(job)))
        self.terminou.emit(dict(job, erro_leitura=task.erro) if task.erro else job)


class DialogoVersionamento(QtWidgets.QDialog):

    def __init__(self, controller, sap, messageFactory=None):
        super(DialogoVersionamento, self).__init__()
        self.controller = controller
        self.sap = sap
        self.messageFactory = messageFactory or UtilsFactory().createMessageFactory()
        self.layoutPrincipal = QtWidgets.QVBoxLayout(self)
        self.setMinimumWidth(480)

    def criarStatus(self):
        self.statusLb = QtWidgets.QLabel('', self)
        self.statusLb.setWordWrap(True)
        self.progressoPb = QtWidgets.QProgressBar(self)
        self.progressoPb.setTextVisible(False)
        self.progressoPb.setVisible(False)
        self.layoutPrincipal.addWidget(self.statusLb)
        self.layoutPrincipal.addWidget(self.progressoPb)
        self.acompanhador = AcompanhadorJob(self.sap, self.statusLb, self.progressoPb, self)
        self.acompanhador.terminou.connect(self.tarefaTerminou)

    def linha(self, texto, widget):
        layout = QtWidgets.QHBoxLayout()
        rotulo = QtWidgets.QLabel(texto, self)
        rotulo.setMinimumWidth(130)
        layout.addWidget(rotulo)
        layout.addWidget(widget, 1)
        self.layoutPrincipal.addLayout(layout)
        return widget

    def showError(self, title, message):
        self.messageFactory.createMessage('ErrorMessageBox').show(self, title, message)

    def showInfo(self, title, message):
        self.messageFactory.createMessage('InfoMessageBox').show(self, title, message)

    def showQuestion(self, title, message):
        return self.messageFactory.createMessage('QuestionMessageBox').show(self, title, message)

    def iniciarTarefa(self, resposta):
        if not resposta:
            return
        jobId = jobIdDaResposta(resposta)
        if not jobId:
            self.showInfo('Aviso', resposta.get('message') or 'Pedido aceito.')
            return
        self.statusLb.setText(resposta.get('message') or '')
        self.acompanhador.iniciar(jobId)

    def tarefaTerminou(self, job):
        if job.get('erro_leitura'):
            self.showError('Aviso', 'O acompanhamento parou: {0}'.format(job['erro_leitura']))
        elif job.get('state') and job.get('state') != 'succeeded':
            self.showError('Aviso', 'A tarefa terminou em {0}.'.format(resumoJob(job)))

    def closeEvent(self, e):
        # Fechar a janela para o acompanhamento; a tarefa no serviço continua e
        # aparece em "Acompanhar Versionamento".
        self.acompanhador.cancelar()
        super(DialogoVersionamento, self).closeEvent(e)


class VersionarLote(DialogoVersionamento):
    # `POST /api/versionamento/lote/:lote_id {dado_producao_id}`: clona a base do
    # dado de produção para o lote (área = UTs do lote com aquele dado).

    def __init__(self, controller, sap):
        super(VersionarLote, self).__init__(controller, sap)
        self.setWindowTitle('Versionar Lote')
        self.lotesCb = self.linha('Lote:', QtWidgets.QComboBox(self))
        self.basesCb = self.linha('Base versionada:', QtWidgets.QComboBox(self))
        self.okBtn = QtWidgets.QPushButton('Versionar', self)
        self.okBtn.clicked.connect(self.versionar)
        self.layoutPrincipal.addWidget(self.okBtn)
        self.criarStatus()
        self.carregar()

    def carregar(self):
        self.lotesCb.clear()
        self.lotesCb.addItem('...', None)
        for lote in sorted(self.sap.getLots(), key=lambda l: (str(l.get('projeto') or ''), str(l.get('nome')))):
            projeto = lote.get('projeto')
            texto = '{0} - {1}'.format(projeto, lote['nome']) if projeto else lote['nome']
            self.lotesCb.addItem(texto, lote['id'])
        self.basesCb.clear()
        self.basesCb.addItem('...', None)
        for dado in self.controller.getSapProductionData():
            if ehBaseVersionada(dado):
                self.basesCb.addItem(rotuloDadoProducao(dado), dado['id'])

    def versionar(self):
        loteId = self.lotesCb.itemData(self.lotesCb.currentIndex())
        dadoId = self.basesCb.itemData(self.basesCb.currentIndex())
        if not ( loteId and dadoId ):
            self.showError('Aviso', 'Escolha o lote e a base versionada!')
            return
        if not self.showQuestion(
                'Atenção',
                'Clonar a base para o lote "{0}"? A tarefa pode levar minutos.'.format(
                    self.lotesCb.currentText()
                )
            ):
            return
        self.iniciarTarefa(self.sap.versionarLote(loteId, dadoId))


class VersionarBloco(DialogoVersionamento):
    # `POST /api/versionamento/bloco/:bloco_id`: clona o repositório do lote
    # para o bloco (área = UTs do bloco).

    def __init__(self, controller, sap):
        super(VersionarBloco, self).__init__(controller, sap)
        self.setWindowTitle('Versionar Bloco')
        self.blocosCb = self.linha('Bloco:', QtWidgets.QComboBox(self))
        self.okBtn = QtWidgets.QPushButton('Versionar', self)
        self.okBtn.clicked.connect(self.versionar)
        self.layoutPrincipal.addWidget(self.okBtn)
        self.criarStatus()
        self.carregar()

    def carregar(self):
        self.blocosCb.clear()
        self.blocosCb.addItem('...', None)
        for bloco in sorted(self.sap.getBlocks(), key=lambda b: str(b.get('nome'))):
            self.blocosCb.addItem(bloco['nome'], bloco['id'])

    def versionar(self):
        blocoId = self.blocosCb.itemData(self.blocosCb.currentIndex())
        if not blocoId:
            self.showError('Aviso', 'Escolha o bloco!')
            return
        if not self.showQuestion(
                'Atenção',
                'Clonar o repositório do lote para o bloco "{0}"? A tarefa pode levar minutos.'.format(
                    self.blocosCb.currentText()
                )
            ):
            return
        self.iniciarTarefa(self.sap.versionarBloco(blocoId))


class AcompanharVersionamento(DialogoVersionamento):
    # `GET /api/versionamento/repositorios`, com a tarefa de cada um, e o
    # descarte com motivo (`POST /api/versionamento/repositorio/:id/descartar`).

    COLUNAS = ['Id', 'Papel', 'Repositório', 'Lote', 'Bloco', 'Atividade', 'Estado', 'Tarefa']

    def __init__(self, controller, sap):
        super(AcompanharVersionamento, self).__init__(controller, sap)
        self.setWindowTitle('Acompanhar Versionamento')
        self.setMinimumWidth(820)
        self.lotesCb = self.linha('Lote:', QtWidgets.QComboBox(self))
        self.blocosCb = self.linha('Bloco:', QtWidgets.QComboBox(self))
        self.tabela = QtWidgets.QTableWidget(0, len(self.COLUNAS), self)
        self.tabela.setHorizontalHeaderLabels(self.COLUNAS)
        self.tabela.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.layoutPrincipal.addWidget(self.tabela)
        botoes = QtWidgets.QHBoxLayout()
        self.atualizarBtn = QtWidgets.QPushButton('Atualizar', self)
        self.acompanharBtn = QtWidgets.QPushButton('Acompanhar tarefa', self)
        self.descartarBtn = QtWidgets.QPushButton('Descartar', self)
        for botao in (self.atualizarBtn, self.acompanharBtn, self.descartarBtn):
            botoes.addWidget(botao)
        self.layoutPrincipal.addLayout(botoes)
        self.atualizarBtn.clicked.connect(self.atualizar)
        self.acompanharBtn.clicked.connect(self.acompanhar)
        self.descartarBtn.clicked.connect(self.descartar)
        self.criarStatus()
        self.repositorios = []
        self.carregarFiltros()
        self.atualizar()

    def carregarFiltros(self):
        self.lotesCb.clear()
        self.lotesCb.addItem('Todos', None)
        for lote in sorted(self.sap.getLots(), key=lambda l: str(l.get('nome'))):
            self.lotesCb.addItem(lote['nome'], lote['id'])
        self.blocosCb.clear()
        self.blocosCb.addItem('Todos', None)
        for bloco in sorted(self.sap.getBlocks(), key=lambda b: str(b.get('nome'))):
            self.blocosCb.addItem(bloco['nome'], bloco['id'])
        self.lotesCb.currentIndexChanged.connect(self.atualizar)
        self.blocosCb.currentIndexChanged.connect(self.atualizar)

    @staticmethod
    def tarefaDaLinha(repo):
        # `versionamento_ctrl.listar` põe `tarefa: {id, estado, progresso,
        # erro}` só na linha viva ainda sem `repo_id` (o clone em curso); nas
        # outras, `tarefa` é nulo e sobra o `job_id`.
        if isinstance(repo.get('tarefa'), dict):
            return resumoJob(repo['tarefa'])
        if repo.get('job_id'):
            return str(repo['job_id'])
        return ''

    def atualizar(self, *args):
        self.repositorios = self.sap.getRepositoriosVersionamento(
            self.lotesCb.itemData(self.lotesCb.currentIndex()),
            self.blocosCb.itemData(self.blocosCb.currentIndex())
        ) or []
        self.tabela.setRowCount(0)
        for repo in self.repositorios:
            idx = self.tabela.rowCount()
            self.tabela.insertRow(idx)
            valores = [
                repo.get('id'), repo.get('papel'), repo.get('repo_id'),
                repo.get('lote_id'), repo.get('bloco_id'), repo.get('atividade_id'),
                repo.get('estado'), self.tarefaDaLinha(repo)
            ]
            for col, valor in enumerate(valores):
                self.tabela.setItem(idx, col, QtWidgets.QTableWidgetItem('' if valor is None else str(valor)))
        self.tabela.resizeColumnsToContents()

    def selecionado(self):
        linhas = self.tabela.selectionModel().selectedRows()
        if not linhas:
            self.showError('Aviso', 'Selecione um repositório!')
            return None
        return self.repositorios[linhas[0].row()]

    def acompanhar(self):
        repo = self.selecionado()
        if not repo:
            return
        if not repo.get('job_id'):
            self.showInfo('Aviso', 'O repositório não tem tarefa registrada.')
            return
        self.acompanhador.iniciar(repo['job_id'])

    def tarefaTerminou(self, job):
        super(AcompanharVersionamento, self).tarefaTerminou(job)
        self.atualizar()

    def descartar(self):
        repo = self.selecionado()
        if not repo:
            return
        motivo, ok = QtWidgets.QInputDialog.getMultiLineText(
            self, 'Descartar repositório',
            'Motivo do descarte de {0} ({1}):'.format(repo.get('repo_id'), repo.get('papel'))
        )
        motivo = (motivo or '').strip()
        if not ok:
            return
        if not motivo:
            self.showError('Aviso', 'O motivo é obrigatório.')
            return
        mensagem = self.sap.descartarRepositorio(repo['id'], motivo)
        if mensagem:
            self.showInfo('Aviso', mensagem)
        self.atualizar()
