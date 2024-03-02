import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddInpuGroupForm(InputDialogV2):

    def __init__(self, sap, parent=None):
        super(AddInpuGroupForm, self).__init__(parent=parent)
        self.sap = sap
        self.currentId = None

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addInpuGroupForm.ui'
        )

    def validInput(self):
        return True

    def getData(self):
        data = {
            'nome' : self.nameLe.text()
        }
        if self.currentId:
            data['id'] = self.currentId
        return data

    def setData(self, currentId, name):
        self.currentId = currentId
        self.nameLe.setText(name)

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos e selecione um arquivo de modelo!')
            return
        try:
            if self.currentId:
                message = self.sap.updateInputGroups([self.getData()])
            else:
                message = self.sap.createInputGroups([self.getData()])
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.close()
