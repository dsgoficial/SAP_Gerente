import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
from qgis import core

class CreateProduct(DockWidget):

    def __init__(self, comboBoxPolygonLayer, sapCtrl):
        super(CreateProduct, self).__init__(controller=sapCtrl)
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.comboBoxPolygonLayer.currentIndexChanged.connect(self.updateAssociatedFields)
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        self.loadLots(self.controller.getSapLots())
        self.updateAssociatedFields(self.comboBoxPolygonLayer.currentIndex())
        self.setWindowTitle('Criar Produtos')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createProduct.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return (
            self.comboBoxPolygonLayer.currentLayer()
            and
            self.getBlockId()
        )

    def updateAssociatedFields(self, currentIndex):
        if currentIndex < 0:
            return
        fields = self.comboBoxPolygonLayer.getCurrentLayerFields()
        for setting in [
                {
                    'combo': self.uuidFieldCb,
                    'fields': fields
                },
                {
                    'combo': self.nameFieldCb,
                    'fields': [''] + fields
                },
                {
                    'combo': self.miFieldCb,
                    'fields': [''] + fields
                },
                {
                    'combo': self.inomFieldCb,
                    'fields': [''] + fields
                },
                {
                    'combo': self.scaleFieldCb,
                    'fields': fields
                },
                {
                    'combo': self.editionCb,
                    'fields': [''] + fields
                }
            ]:
            combo = setting['combo']
            combo.clear()
            combo.addItems(setting['fields'])

    def getAssociatedFields(self):
        return {
            'uuid': self.uuidFieldCb.currentText(),
            'nome': self.nameFieldCb.currentText(),
            'mi': self.miFieldCb.currentText(),
            'inom': self.inomFieldCb.currentText(),
            'denominador_escala': self.scaleFieldCb.currentText(),
            'edicao': self.editionCb.currentText()
        }

    def loadLots(self, lots):
        self.lotCb.clear()
        self.lotCb.addItem('...', None)
        for lot in lots:
            self.lotCb.addItem(
                lot['nome'], 
                lot['id']
            )

    def getBlockId(self):
        return self.lotCb.itemData(self.lotCb.currentIndex())

    def runFunction(self):
        layer = self.comboBoxPolygonLayer.currentLayer()
        if len([ f for f in layer.getFeatures() if f.geometry().wkbType() != core.QgsWkbTypes.MultiPolygon ]) != 0:
            self.showError('Aviso', 'A camada deve ser do tipo "MultiPolygon"!')
            return
        self.controller.createSapProducts(
            layer, 
            self.getBlockId(), 
            self.getAssociatedFields(), 
            self.onlySelectedCkb.isChecked()
        )