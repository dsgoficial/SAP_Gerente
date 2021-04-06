import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

from Ferramentas_Gerencia.interfaces.IDockWidget  import IDockWidget
from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory

class DockWidget(QtWidgets.QWidget, IDockWidget):

    def __init__(self, 
            controller,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(DockWidget, self).__init__()
        self.controller = controller
        uic.loadUi(self.getUiPath(), self)

    def loadIconBtn(self, button, pathIcon, toolTip):
        button.setIcon(QtGui.QIcon(pathIcon))
        button.setIconSize(QtCore.QSize(24,24))
        button.setToolTip(toolTip)
      
    def getUiPath(self):
        raise NotImplementedError()

    def runFunction(self):
        raise NotImplementedError()

    def validInput(self):
        raise NotImplementedError()

    def clearInput(self):
        raise NotImplementedError()
        
    def showErrorMessageBox(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)
        
    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showMessageErro('Aviso', "<p>Preencha todos os campos!</p>")
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.runFunction()
            self.clearInput()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()