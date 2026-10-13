import os, sys, copy
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from .inputDialogV2  import InputDialogV2 
 
class CreateDefaultSteps(InputDialogV2):

    def __init__(self, sapCtrl):
        super(CreateDefaultSteps, self).__init__(controller=sapCtrl)
        self.loadProjects(self.controller.getSapProjects())
        self.loadDefaults()
        self.setWindowTitle('Criar Etapas Padrão')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createDefaultSteps.ui"
        )

    def loadDefaults(self):
        self.defaultCb.clear()
        for d in [
            {
                'nome': 'Sem controle de qualidade nas subfases',
                'id': 1
            },
            {
                'nome': 'Uma Revisão/Correção em todas as subfases',
                'id': 2
            },
            {
                'nome': 'Uma Revisão em todas as subfases',
                'id': 3
            }
        ]:
            self.defaultCb.addItem(d['nome'], d['id'])

    def loadProjects(self, data):
        self.projectsCb.clear()
        self.projectsCb.addItem('...', None)
        for d in data:
            self.projectsCb.addItem(d['nome'], d['id'])

    @QtCore.pyqtSlot(int)
    def on_projectsCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.lotsCb.clear()
            return
        self.loadLots(self.projectsCb.currentText())

    def loadLots(self, projectName):
        # SAP 3.0: o lote é do acervo e não tem linha de produção; o par
        # (lote, linha) NASCE da etapa. Por isso o lote vem da lista de lotes do
        # projeto (e não das subfases, onde o lote novo, sem etapa, não aparece)
        # e a fase pode ser de qualquer linha.
        projectId = self.projectsCb.itemData(self.projectsCb.currentIndex())
        lots = [
            l for l in self.controller.getSapLots()
            if l.get('projeto_id') == projectId or l.get('projeto') == projectName
        ]
        self.lotsCb.clear()
        self.lotsCb.addItem('...', None)
        for lot in sorted(lots, key=lambda l: l['nome']):
            self.lotsCb.addItem(lot['nome'], lot['id'])

    @QtCore.pyqtSlot(int)
    def on_lotsCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.phasesCb.clear()
            return
        self.loadPhases()

    def loadPhases(self):
        phases = self.controller.getSapPhases()
        self.phasesCb.clear()
        self.phasesCb.addItem('...', None)
        for step in sorted(phases, key=lambda f: (f['linha_producao'], f['ordem'])):
            self.phasesCb.addItem('{0} - {1}'.format(step['linha_producao'], step['fase']), str(step['fase_id']))

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not (
                self.lotsCb.itemData(self.lotsCb.currentIndex())
                and
                self.phasesCb.itemData(self.phasesCb.currentIndex())
            ):
            self.showError('Erro', 'Preencha todos os dados!')
            return

        try:
            message = self.controller.createDefaultStep(
                int(self.defaultCb.itemData(self.defaultCb.currentIndex())),
                int(self.phasesCb.itemData(self.phasesCb.currentIndex())),
                int(self.lotsCb.itemData(self.lotsCb.currentIndex()))
            )
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))