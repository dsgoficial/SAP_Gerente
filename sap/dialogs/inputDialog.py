import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.sap.interfaces.IInputDialog  import IInputDialog
from Ferramentas_Gerencia.sap.factory.messageSingleton  import MessageSingleton

class InputDialog(QtWidgets.QDialog, IInputDialog):
    
    def __init__(self, parent):
        super(InputDialog, self).__init__(parent=parent)
        uic.loadUi(self.getUiPath(), self)

    def getUiPath(self):
        raise NotImplementedError()

    def getData(self):
        raise NotImplementedError()

    def clearInput(self):
        raise NotImplementedError()

    def showEvent(self, e):
        self.clearInput()

    def showError(self, title, text):
        MessageSingleton.getInstance().showError(
            self,
            title, 
            text
        )

    def showInfo(self, title, text):
        MessageSingleton.getInstance().showInfo(
            self,
            title, 
            text
        )

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.reject()