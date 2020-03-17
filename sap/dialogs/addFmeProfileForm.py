import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dialogs.inputDialog  import InputDialog

class AddFmeProfileForm(InputDialog):

    def __init__(self, sapCtrl, parent=None):
        super(AddFmeProfileForm, self).__init__(parent)
        self.sapCtrl = sapCtrl

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addFmeProfileForm.ui'
        )

    def loadFmeServers(self, servers):
        self.fmeServersCb.clear()
        self.fmeServersCb.addItem('...', None)
        for server in servers:
            self.fmeServersCb.addItem(server['servidor'], server)

    def loadSubphases(self, subphases):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        for subphase in subphases:
            self.subphaseCb.addItem(subphase['nome'], subphase['id'])

    def loadRoutines(self, routines):
        self.fmeRoutinesCb.clear()
        self.fmeRoutinesCb.addItem('...', None)
        for routine in routines:
            self.fmeRoutinesCb.addItem(routine['rotina'], routine['id'])

    def clearInput(self):
        self.fmeServersCb.setCurrentIndex(0)
        self.subphaseCb.setCurrentIndex(0)
        self.fmeRoutinesCb.clear()
        self.fmeRoutinesCb.addItem('...', None)
        self.completionCkb.setChecked(False)
        self.falsePositiveCkb.setChecked(False)
    
    def validInput(self):
        return (
            self.fmeServersCb.currentIndex() != 0
            and
            self.subphaseCb.currentIndex() != 0
            and
            self.fmeRoutinesCb.currentIndex() != 0
        )

    def getData(self):
        return {
            'gerenciador_fme_id': self.fmeServersCb.itemData(self.fmeServersCb.currentIndex())['id'],
            'rotina': self.fmeRoutinesCb.itemData(self.fmeRoutinesCb.currentIndex()),
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex()),
            'requisito_finalizacao': self.completionCkb.isChecked(),
            'gera_falso_positivo': self.falsePositiveCkb.isChecked()
        }

    @QtCore.pyqtSlot(int)
    def on_fmeServersCb_currentIndexChanged(self, idx):
        serverData = self.fmeServersCb.itemData(idx)
        if not serverData:
            return
        self.loadRoutines(self.sapCtrl.getFmeRoutines(serverData['servidor'], serverData['porta']))

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()