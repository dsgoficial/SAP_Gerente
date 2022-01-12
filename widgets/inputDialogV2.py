import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.interfaces.IInputDialog  import IInputDialog
from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory

class InputDialogV2(QtWidgets.QDialog):
    
    def __init__(self,
            controller=None,
            parent=None, 
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(InputDialogV2, self).__init__(parent=parent)
        uic.loadUi(self.getUiPath(), self)
        self.messageFactory = messageFactory
        self.controller = controller

    def setController(self, controller):
        self.controller = controller

    def getController(self):
        return self.controller

    def showError(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showInfo(self, title, text):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)