import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddRuleProfileLotForm(InputDialog):

    def __init__(self, sap, selected, parent=None):
        super(AddRuleProfileLotForm, self).__init__(parent=parent)
        self.sap = sap
        self.selected = selected
        self.loadLots(self.sap.getLots())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addRuleProfileLotForm.ui'
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
            self.sap.createRuleProfiles(self.getData())
            self.showInfo('Aviso', 'Salvo com sucesso!')
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()