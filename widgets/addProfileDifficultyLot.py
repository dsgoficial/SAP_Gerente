import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddProfileDifficultyLot(InputDialogV2):

    def __init__(self, sap, selected, parent=None):
        super(AddProfileDifficultyLot, self).__init__(parent=parent)
        self.sap = sap
        self.selected = selected
        lotIds = [s['lote_id'] for s in selected]
        self.loadLots([
            l
            for l in self.sap.getLots()
            if not(l['id'] in lotIds)
        ])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProfileDifficultyLot.ui'
        )

    def loadLots(self, lots):
        self.lotsCb.clear()
        self.lotsCb.addItem('...', None)
        for lot in lots:
            self.lotsCb.addItem(lot['nome'], lot['id'])

    def clearInput(self):
        self.lotsCb.setCurrentIndex(0)

    def validInput(self):
        return self.lotsCb.currentIndex() != 0

    def getData(self):
        data = []
        for s in self.selected:
            s['lote_id'] = int(self.lotsCb.itemData(self.lotsCb.currentIndex()))
            data.append(s)
        return data

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.sap.createProfileDifficulty(self.getData())
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showInfo('Aviso', 'Salvo com sucesso!')
            self.accept()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Aviso', str(e))