import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory

class ResetPropertiesUT(QtWidgets.QDialog):

    def __init__(self, 
            controller, 
            qgis, 
            sap,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(ResetPropertiesUT, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.messageFactory = messageFactory
        self.loadIconBtn(self.extractFieldBtn, self.getExtractIconPath(), 'Extrair valores mediante seleções')
        self.setWindowTitle('Redefinir Propriedades da Unidade de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "resetPropertiesUT.ui"
        )

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

    def showError(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showInfo(self, title, message):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)

    @QtCore.pyqtSlot(bool)
    def on_extractFieldBtn_clicked(self):
        values = self.controller.getValuesFromLayer('resetEstimatedTimeAndDifficultys', 'activity')
        self.workspacesIdLe.setText(values)
        
    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', "<p>Preencha todas as entradas ou entrada inválida!</p>")
            return
        workspacesIds = self.getWorkspacesIds()
        print(self.getData())
        #self.sap.resetPropertiesUT(self.getData())
        self.showInfo('Aviso', 'Executado com sucesso!')

    def validInput(self):
        return (
            self.workspacesIdLe.text()
            and
            (
                not(self.difficultySb.value() is None)
                or
                not(self.timeSb.value() is None)
                or
                not(self.prioritySb.value() is None)
            )
        )

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdLe.text().split(',') if d ]

    def getData(self):
        data = []
        for wId in self.getWorkspacesIds():
            row = {'id': wId}
            if not(self.difficultySb.value() is None):
                row['dificuldade'] = self.difficultySb.value()
            if not(self.timeSb.value() is None):
                row['tempo_estimado_minutos'] = self.timeSb.value()
            if not(self.prioritySb.value() is None):
                row['prioridade'] = self.prioritySb.value()
            data.append(row)
        return data