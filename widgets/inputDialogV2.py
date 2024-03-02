import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory
import socket

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
        self.currentId = None
        self.editMode = False

    def activeEditMode(self, b):
        self.editMode = b

    def isEditMode(self):
        return self.editMode

    def setCurrentId(self, currentId):
        self.currentId = currentId
    
    def getCurrentId(self):
        return self.currentId

    def setController(self, controller):
        self.controller = controller

    def getController(self):
        return self.controller

    def showError(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showInfo(self, title, message):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)

    def closeEvent(self, e):
        self.closeChildren(QtWidgets.QDialog)
        super().closeEvent(e)

    def closeChildren(self, typeWidget):
        [ d.close() for d in self.findChildren(typeWidget) ]

    def isOpenConnection(self, ip, port):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, port))
        isOpen = False
        if result == 0:
            isOpen = True
        sock.close()
        QtWidgets.QApplication.restoreOverrideCursor()
        return isOpen