import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialog  import InputDialog

class AddFmeProfileForm(InputDialog):

    def __init__(self, sap, fme, parent=None):
        super(AddFmeProfileForm, self).__init__(parent=parent)
        self.sap = sap
        self.fme = fme
        self.orderLe.setValidator(QtGui.QIntValidator(0, 1000))
        self.loadFmeServers(self.sap.getFmeServers())
        self.loadSubphases(self.sap.getSubphases())
        self.loadLots(self.sap.getLots())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addFmeProfileForm.ui'
        )

    def loadLots(self, lots):
        self.lotCb.clear()
        self.lotCb.addItem('...', None)
        for lot in lots:
            self.lotCb.addItem(lot['nome'], lot['id'])

    def loadFmeServers(self, servers):
        self.fmeServersCb.clear()
        self.fmeServersCb.addItem('...', None)
        for server in servers:
            self.fmeServersCb.addItem(server['url'], server['id'])

    def loadSubphases(self, subphases):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        for subphase in subphases:
            self.subphaseCb.addItem(subphase['subfase'], subphase['subfase_id'])

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
        self.orderLe.setText('')
    
    def validInput(self):
        return (
            self.fmeServersCb.currentIndex() != 0
            and
            self.subphaseCb.currentIndex() != 0
            and
            self.fmeRoutinesCb.currentIndex() != 0
            and
            self.orderLe.text() != ''
        )

    def getData(self):
        return {
            'gerenciador_fme_id': self.fmeServersCb.itemData(self.fmeServersCb.currentIndex()),
            'rotina': self.fmeRoutinesCb.itemData(self.fmeRoutinesCb.currentIndex()),
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex()),
            'requisito_finalizacao': self.completionCkb.isChecked(),
            'gera_falso_positivo': self.falsePositiveCkb.isChecked(),
            'ordem': int(self.orderLe.text()),
            'lote_id': self.lotCb.itemData(self.lotCb.currentIndex())
        }

    @QtCore.pyqtSlot(int)
    def on_fmeServersCb_currentIndexChanged(self, idx):
        serverUrl = self.fmeServersCb.itemText(idx)
        if not self.fmeServersCb.itemData(idx):
            return
        self.loadRoutines(
            self.fme.getRoutines(serverUrl)
        )

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        try:
            message = self.sap.createFmeProfiles(
                [self.getData()]
            )
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))