import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.dialogs.inputDialog  import InputDialog

class AddStyleForm(InputDialog):

    def __init__(self, parent=None):
        super(AddStyleForm, self).__init__(parent)
        

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addStyleForm.ui'
        )
        
    def clearInput(self):
        pass

    def validInput(self):
        return self.styleNameLe.text()

    def getData(self):
        return {
            'styleName' : self.styleNameLe.text()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Informe um nome de estilo')
            return
        self.accept()