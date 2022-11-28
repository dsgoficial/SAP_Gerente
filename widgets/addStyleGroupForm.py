import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddStyleGroupForm(InputDialog):

    def __init__(self, parent=None):
        super(AddStyleGroupForm, self).__init__(parent=parent)
        

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addStyleGroupForm.ui'
        )
        
    def clearInput(self):
        pass

    def validInput(self):
        return self.styleNameLe.text()

    def getData(self):
        return {
            'nome' : self.styleNameLe.text()
        }

    def setData(self, name):
        self.styleNameLe.setText(name)

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Informe o nome do grupo')
            return
        self.accept()