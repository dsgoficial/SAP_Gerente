import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory

class DockWidgetAutoComplete(QtWidgets.QDialog):

    def __init__(self, 
            controller,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(DockWidgetAutoComplete, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.controller = controller
        self.messageFactory = messageFactory
        self.loadIconBtn(self.extractFieldBtn, self.getExtractIconPath(), 'Extrair valores mediante seleções')

    def loadIconBtn(self, button, pathIcon, toolTip):
        button.setIcon(QtGui.QIcon(pathIcon))
        button.setIconSize(QtCore.QSize(24,24))
        button.setToolTip(toolTip)

    def getExtractIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'extract.png'
        )
        
    def showErrorMessageBox(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    @QtCore.pyqtSlot(bool)
    def on_extractFieldBtn_clicked(self):
        self.autoCompleteInput()
        
    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showErrorMessageBox('Aviso', "<p>Preencha todos os campos!</p>")
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.runFunction()
            self.clearInput()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    