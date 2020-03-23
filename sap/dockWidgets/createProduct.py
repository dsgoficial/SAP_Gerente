import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidget  import DockWidget
 
class CreateProduct(DockWidget):

    def __init__(self, comboBoxPolygonLayer, sapCtrl):
        super(CreateProduct, self).__init__(sapCtrl=sapCtrl)
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)

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
        return True

    def getLayer(self):
        return self.comboBoxPolygonLayer.currentLayer()

    def runFunction(self):
        print(self.getLayer())