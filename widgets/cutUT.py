import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory
from qgis import core, gui
from qgis.utils import iface

class CutUT(QtWidgets.QDialog):

    def __init__(self, 
            controller, 
            qgis, 
            sap,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(CutUT, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.messageFactory = messageFactory
        self.loadIconBtn(self.extractFieldBtn, self.getExtractIconPath(), 'Extrair valores mediante seleções')
        self.loadIconBtn(self.extractEWKTBtn, self.getExtractIconPath(), 'Extrair valores mediante seleções')
        self.setWindowTitle('Cortar Unidade de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "cutUT.ui"
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
        if not len(selectedFeatures) > 1:
            self.showError('Aviso', "Selecione no mínimo duas feições de reshape!")
            return
        ewkts = []
        for feat in selectedFeatures:
            ewkt = self.qgis.geometryToEwkt( feat.geometry(), layer.crs().authid(), 'EPSG:4326' )
            ewkts.append(ewkt)
        self.ewktLe.setText('|'.join(ewkts))

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
        self.sap.cutUT(
            self.getWorkspacesId(),
            self.getEWKTs()
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

    def getEWKTs(self):
        return [ d for d in self.ewktLe.text().split('|') if d ]

    def isValidEWKT(self):
        ewkts = self.getEWKTs()
        if not ewkts:
            return False
        for ewkt in ewkts:
            geom = core.QgsGeometry().fromWkt(ewkt.split(';')[1])
            if not geom.isGeosValid():
                return False
        return True