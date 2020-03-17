import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidget  import DockWidget
 
class CreateWorkUnit(DockWidget):

    def __init__(self, sapCtrl):
        super(CreateWorkUnit, self).__init__(sapCtrl=sapCtrl)
        self.sapCtrl = sapCtrl
        self.layerNameLe.setText('camada')
        self.prefixFeatureLe.setText('Teste')
        self.xSizeLe.setValue(5000)
        self.ySizeLe.setValue(8000)
        self.overlapLe.setValue(200)
        self.deplaceLe.setValue(500)
        #self.onlySelectedCkb.setChecked('')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createWorkUnit.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def getInputData(self):
        return {
            'layerName' : self.layerNameLe.text(),
            'xSize' : self.xSizeLe.value(),
            'ySize' : self.ySizeLe.value(),
            'overlap' : self.overlapLe.value(),
            'deplace' : self.deplaceLe.value(),
            'prefixFeature' : self.prefixFeatureLe.text(),
            'onlySelected' : self.onlySelectedCkb.isChecked()
        }

    def runFunction(self):
        inputData = self.getInputData()
        self.sapCtrl.createWorkUnit(
            inputData['layerName'],
            (inputData['xSize'], inputData['ySize']),
            inputData['overlap'],
            inputData['deplace'],
            inputData['prefixFeature'],
            inputData['onlySelected']
            
        )
