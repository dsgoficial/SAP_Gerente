import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory

class DockWidget(QtWidgets.QDialog):

    def __init__(self, 
            controller,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(DockWidget, self).__init__()
        self.messageFactory = messageFactory
        self.controller = controller
        uic.loadUi(self.getUiPath(), self)

    def loadIconBtn(self, button, pathIcon, toolTip):
        button.setIcon(QtGui.QIcon(pathIcon))
        button.setIconSize(QtCore.QSize(24,24))
        button.setToolTip(toolTip)
        
    def showErrorMessageBox(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showError(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showInfo(self, title, message):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)
        
    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        """ if not self.validInput():
            self.showErrorMessageBox('Aviso', "<p>Preencha todos os campos!</p>")
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.runFunction()
            self.clearInput()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor() """
        self.runFunction()
        self.clearInput()