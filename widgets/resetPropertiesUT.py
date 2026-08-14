import os, sys, copy
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
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
        self.setupFields()

    def setupFields(self):
        """Cada campo só entra no envio se o operador marcar 'Alterar'.
        Sem isso o QSpinBox não tocado mandaria 0, e o servidor sobrescreveria
        dificuldade, tempo estimado e prioridade das UTs em silêncio. Prioridade 0
        é o topo da fila (ORDER BY ut_prioridade), então o estrago seria calado.
        """
        for spinBox, checkBox, maximum in self.getFields():
            spinBox.setRange(0, maximum)
            spinBox.setEnabled(False)
            checkBox.setChecked(False)
            checkBox.toggled.connect(spinBox.setEnabled)

    def getFields(self):
        return [
            (self.difficultySb, self.difficultyCkb, 1000),
            (self.timeSb, self.timeCkb, 1000000),
            (self.prioritySb, self.priorityCkb, 1000000)
        ]

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
        try:
            if not self.validInput():
                self.showError('Aviso', "<p>Informe os IDs e marque ao menos um campo para alterar!</p>")
                return
            data = self.getData()
            message = self.sap.resetPropertiesUT(data)
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))

    def validInput(self):
        return (
            self.getWorkspacesIds()
            and
            any(checkBox.isChecked() for _, checkBox, _ in self.getFields())
        )

    def getWorkspacesIds(self):
        try:
            return [ int(d) for d in self.workspacesIdLe.text().split(',') if d.strip() ]
        except ValueError:
            return []

    def getData(self):
        columns = [
            ('dificuldade', self.difficultySb, self.difficultyCkb),
            ('tempo_estimado_minutos', self.timeSb, self.timeCkb),
            ('prioridade', self.prioritySb, self.priorityCkb)
        ]
        data = []
        for wId in self.getWorkspacesIds():
            row = {'id': wId}
            for name, spinBox, checkBox in columns:
                if checkBox.isChecked():
                    row[name] = spinBox.value()
            data.append(row)
        return data