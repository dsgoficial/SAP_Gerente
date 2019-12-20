import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.sap.views.dialogs.interfaces.IInputDialog  import IInputDialog

class InputDialog(QtWidgets.QDialog, IInputDialog):
    
    def __init__(self, parent):
        super(InputDialog, self).__init__(parent=parent)
        uic.loadUi(self.getUiPath(), self)

    def getUiPath(self):
        raise NotImplementedError()

    def getData(self):
        raise NotImplementedError()

    def showMessageErro(self, title, text):
        QtWidgets.QMessageBox.critical(
            self,
            title, 
            text
        )