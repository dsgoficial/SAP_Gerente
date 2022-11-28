import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from .inputDialogV2  import InputDialogV2 

class GeneratesWorkUnit(InputDialogV2):

    def __init__(self, comboBoxPolygonLayer, sapCtrl):
        super(GeneratesWorkUnit, self).__init__(controller=sapCtrl)
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        #self.layerNameLe.setText('camada')
        self.prefixFeatureLe.setText('Teste')
        self.xSizeLe.setValue(5000)
        self.ySizeLe.setValue(8000)
        self.overlapLe.setValue(200)
        self.deplaceLe.setValue(500)
        #self.onlySelectedCkb.setChecked('')
        self.setWindowTitle('Gerar Unidades de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "generatesWorkUnit.ui"
        )

    def getData(self):
        return {
            'layerName' : self.comboBoxPolygonLayer.currentLayer().name(),
            'xSize' : self.xSizeLe.value(),
            'ySize' : self.ySizeLe.value(),
            'overlap' : self.overlapLe.value(),
            'deplace' : self.deplaceLe.value(),
            'prefixFeature' : self.prefixFeatureLe.text(),
            'onlySelected' : self.onlySelectedCkb.isChecked()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        inputData = self.getData()
        try:
            self.controller.createWorkUnit(
                inputData['layerName'],
                (inputData['xSize'], inputData['ySize']),
                inputData['overlap'],
                inputData['deplace'],
                inputData['prefixFeature'],
                inputData['onlySelected']
                
            )
            self.showInfo('Aviso', 'Unidades de trabalho geradas com sucesso!')
        except Exception as e:
            self.showError('Aviso', str(e))
