import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory

class DockWidgetV2(QtWidgets.QWidget):

    def __init__(self, 
            controller,
            parent=None,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(DockWidgetV2, self).__init__(parent=parent)
        self.messageFactory = messageFactory
        self.controller = controller
        self.parent = parent
        uic.loadUi(self.getUiPath(), self)

    def getUiPath(self):
        raise NotImplementedError()

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