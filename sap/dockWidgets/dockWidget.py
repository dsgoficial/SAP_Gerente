import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

from Ferramentas_Gerencia.sap.interfaces.IDockWidget  import IDockWidget

class DockWidget(QtWidgets.QWidget, IDockWidget):

    def __init__(self, sapCtrl):
        super(DockWidget, self).__init__(sapCtrl=sapCtrl)
        uic.loadUi(self.getUiPath(), self)
      
    def getUiPath(self):
        raise NotImplementedError()

    def runFunction(self):
        raise NotImplementedError()

    def validInput(self):
        raise NotImplementedError()

    def clearInput(self):
        raise NotImplementedError()
        
    def showMessageErro(self, title, text):
        QtWidgets.QMessageBox.critical(
            self,
            title, 
            text
        )
        
    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showMessageErro('Aviso', "<p>Preencha todos os campos!</p>")
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.runFunction()
        self.clearInput()
        QtWidgets.QApplication.restoreOverrideCursor()