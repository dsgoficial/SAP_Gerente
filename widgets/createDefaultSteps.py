import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
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
        steps = self.controller.getSapStepsByTag(tag='lote', sortByTag='lote', tagFilter=('projeto', projectName))
        self.lotsCb.clear()
        self.lotsCb.addItem('...', None)
        for step in steps:
            self.lotsCb.addItem(step['lote'], step['lote_id'])
    
    @QtCore.pyqtSlot(int)
    def on_lotsCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.phasesCb.clear()
            return
        lotId = self.lotsCb.itemData(currentIndex)
        lots = self.controller.getSapStepsByTag(tag='lote', sortByTag='lote', tagFilter=('projeto', self.projectsCb.currentText()))
        select = [ l for l in lots if l['lote_id'] == lotId]
        self.loadPhases(select[0]['linha_producao_id'])

    def loadPhases(self, productLineId):
        phases = self.controller.getSapPhases()
        phases = [ s for s in phases if s['linha_producao_id'] == productLineId ]
        self.phasesCb.clear()
        self.phasesCb.addItem('...', None)
        for step in phases:
            self.phasesCb.addItem(step['fase'], str(step['fase_id']))

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
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))