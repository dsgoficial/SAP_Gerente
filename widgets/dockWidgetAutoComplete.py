import os, sys, copy
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui

from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory

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

    def showInfoMessageBox(self, title, message):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)  
        
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
    def on_extractFieldBtn_clicked(self):
        self.autoCompleteInput()
        
    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showErrorMessageBox('Aviso', "<p>Preencha todos os campos!</p>")
            return
        resultado = self.runFunction()
        # False: a chamada falhou e o erro já foi mostrado. Um dicionário traz o
        # texto do servidor (pausar, reiniciar e voltar, com a revogação).
        if resultado is False:
            return
        if isinstance(resultado, dict):
            if resultado.get('alerta'):
                self.showError('Aviso', resultado.get('texto') or '')
            else:
                self.showInfo('Aviso', resultado.get('texto') or 'Executado com sucesso!')
        else:
            self.showInfo('Aviso', 'Executado com sucesso!')
        self.clearInput()

    