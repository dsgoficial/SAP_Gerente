import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

from Ferramentas_Gerencia.sap.views.dockWidgets.interface.IDockWidget  import IDockWidget

class DockWidgetAutoComplete(QtWidgets.QWidget, IDockWidget):

    def __init__(self, sapCtrl):
        super(DockWidgetAutoComplete, self).__init__(sapCtrl=sapCtrl)
        uic.loadUi(self.getUiPath(), self)
        self.extract_field_btn.setIcon(QtGui.QIcon(self.getIconPath()))
        self.extract_field_btn.setIconSize(QtCore.QSize(24,24))
        self.extract_field_btn.setToolTip('Extrair valores mediante seleções')
    
    def getUiPath(self):
        raise NotImplementedError()

    def runFunction(self):
        raise NotImplementedError()

    def autoCompleteInput(self):
        raise NotImplementedError()

    def validInput(self):
        raise NotImplementedError()

    def showMessageErro(self):
        raise NotImplementedError()

    def getIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'extract.png'
        )
        
    def showMessageErro(self, title, text):
        QtWidgets.QMessageBox.critical(
            self,
            title, 
            text
        )

    @QtCore.pyqtSlot(bool)
    def on_extract_field_btn_clicked(self):
        self.autoCompleteInput()
        
    @QtCore.pyqtSlot(bool)
    def on_ok_btn_clicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if not self.validInput():
            self.showMessageErro('Aviso', "<p>Preencha todos os campos!</p>")
            return
        self.runFunction()
        QtWidgets.QApplication.restoreOverrideCursor()

    