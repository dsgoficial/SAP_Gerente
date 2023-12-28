import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory
from qgis import core, gui
from qgis.utils import iface

class ReshapeUT(QtWidgets.QDialog):

    def __init__(self, 
            controller, 
            qgis, 
            sap,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(ReshapeUT, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.messageFactory = messageFactory
        self.loadIconBtn(self.extractFieldBtn, self.getExtractIconPath(), 'Extrair valores mediante seleções')
        self.loadIconBtn(self.extractEWKTBtn, self.getExtractIconPath(), 'Extrair valores mediante seleções')
        self.setWindowTitle('Redesenhar Unidade de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "reshapeUT.ui"
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
    def on_extractEWKTBtn_clicked(self):
        layer = iface.activeLayer()
        selectedFeatures = layer.selectedFeatures()
        if len(selectedFeatures) != 1:
            self.showError('Aviso', "Selecione apenas uma feição de reshape!")
            return
        feat = selectedFeatures[0]
        ewkt = self.qgis.geometryToEwkt( feat.geometry(), layer.crs().authid(), 'EPSG:4326' )
        self.ewktLe.setText(ewkt)

    @QtCore.pyqtSlot(bool)
    def on_extractFieldBtn_clicked(self):
        values = self.controller.getValuesFromLayer('editUT', 'workUnit')
        if len(values.split(',')) != 1:
            self.showError('Aviso', "Selecione apenas uma unidade de trabalho!")
            return
        self.workspacesIdLe.setText(values)
        
    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', "<p>Preencha todas as entradas ou entrada inválida!</p>")
            return
        self.sap.reshapeUT(
            self.getWorkspacesId(),
            self.ewktLe.text()
        )
        self.showInfo('Aviso', 'Executado com sucesso!')

    def validInput(self):
        return (
            self.workspacesIdLe.text()
            and
            self.isValidEWKT()
        )

    def getWorkspacesId(self):
        return int(self.workspacesIdLe.text())

    def isValidEWKT(self):
        ewkt = self.ewktLe.text()
        if not ewkt:
            return False
        geom = core.QgsGeometry().fromWkt(ewkt.split(';')[1])
        return geom.isGeosValid()