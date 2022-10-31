import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddFmeServerForm(InputDialog):

    def __init__(self, parent=None):
        super(AddFmeServerForm, self).__init__(parent)

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
        self.accept()