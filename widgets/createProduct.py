import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class CreateProduct(DockWidget):

    def __init__(self, comboBoxPolygonLayer, sapCtrl):
        super(CreateProduct, self).__init__(controller=sapCtrl)
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.comboBoxPolygonLayer.currentIndexChanged.connect(self.updateAssociatedFields)
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        self.loadProductionLines(self.controller.getSapProductionLines())
        self.updateAssociatedFields(self.comboBoxPolygonLayer.currentIndex())

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
            self.getProductionLineId()
        )

    def updateAssociatedFields(self, currentIndex):
        if currentIndex < 0:
            return
        fields = self.comboBoxPolygonLayer.getCurrentLayerFields()
        for combo in [
                self.uuidFieldCb,
                self.nameFieldCb,
                self.miFieldCb,
                self.inomFieldCb,
                self.scaleFieldCb,
            ]:
            combo.clear()
            combo.addItems(fields)

    def getAssociatedFields(self):
        return {
            'uuid': self.uuidFieldCb.currentText(),
            'nome': self.nameFieldCb.currentText(),
            'mi': self.miFieldCb.currentText(),
            'inom': self.inomFieldCb.currentText(),
            'escala': self.scaleFieldCb.currentText()
        }

    def loadProductionLines(self, productionLines):
        self.productionLinesCb.clear()
        self.productionLinesCb.addItem('...', None)
        for productionLine in productionLines:
            self.productionLinesCb.addItem(
                "{0} - {1}".format(productionLine['projeto'], productionLine['nome']), 
                productionLine['id']
            )

    def getProductionLineId(self):
        return self.productionLinesCb.itemData(self.productionLinesCb.currentIndex())

    def runFunction(self):
        self.controller.createSapProducts(
            self.comboBoxPolygonLayer.currentLayer(), 
            self.getProductionLineId(), 
            self.getAssociatedFields(), 
            self.onlySelectedCkb.isChecked()
        )