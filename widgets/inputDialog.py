import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory

class InputDialog(QtWidgets.QDialog):
    
    def __init__(self, 
            parent, 
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(InputDialog, self).__init__(parent=parent)
        uic.loadUi(self.getUiPath(), self)
        self.messageFactory = messageFactory

    def getUiPath(self):
        raise NotImplementedError()

    def getData(self):
        raise NotImplementedError()

    def clearInput(self):
        raise NotImplementedError()

    def showEvent(self, e):
        self.clearInput()

    def showError(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showInfo(self, title, text):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.reject()