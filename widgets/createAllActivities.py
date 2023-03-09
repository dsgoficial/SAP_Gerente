import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from .inputDialogV2  import InputDialogV2 

class CreateAllActivities(InputDialogV2):

    def __init__(self, sapCtrl):
        super(CreateAllActivities, self).__init__(controller=sapCtrl)
        self.loadProjects(self.controller.getSapProjects())
        self.setWindowTitle('Criar Todas as Atividades')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createAllActivities.ui"
        )

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

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not (
                self.projectsCb.itemData(self.projectsCb.currentIndex())
                and
                self.lotsCb.itemData(self.lotsCb.currentIndex())
            ):
            self.showError('Erro', 'Preencha todos os dados!')
            return

        try:
            message = self.controller.createAllActivities(
                self.lotsCb.itemData(self.lotsCb.currentIndex())
            )
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))