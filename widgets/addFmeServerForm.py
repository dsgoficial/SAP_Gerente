import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialog  import InputDialog

class AddFmeServerForm(InputDialog):

    def __init__(self, 
            sap,
            parent=None
        ):
        super(AddFmeServerForm, self).__init__(parent=parent)
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addFmeServerForm.ui'
        )

    def clearInput(self):
        self.urlLe.setText('')
    
    def validInput(self):
        return (
            self.urlLe.text()
        )

    def getData(self):
        return {
            'url': self.urlLe.text()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        try:
            message = self.sap.createFmeServers([self.getData()])
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))