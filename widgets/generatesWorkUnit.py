import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from .inputDialogV2  import InputDialogV2 

class GeneratesWorkUnit(InputDialogV2):

    def __init__(
            self, 
            comboBoxPolygonLayer,
            comboBoxProjection, 
            controller,
            sap,
            qgis
        ):
        super(GeneratesWorkUnit, self).__init__(controller=controller)
        self.sap = sap
        self.qgis = qgis
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        self.comboBoxProjection = comboBoxProjection
        self.comboBoxProjection.setFixedSize(QtCore.QSize(250, 25))
        self.epsgLayout.addWidget(self.comboBoxProjection)
        #self.layerNameLe.setText('camada')
        self.xSizeLe.setValue(5000)
        self.ySizeLe.setValue(8000)
        self.overlapLe.setValue(200)
        self.deplaceLe.setValue(500)
        #self.onlySelectedCkb.setChecked('')
        self.setWindowTitle('Gerar Unidades de Trabalho Avançado')
        self.loadCombo(
            self.blocksCb, 
            [ 
                {'value': d['nome'], 'id': d['id']}
                for d in self.sap.getBlocks()
            ]
        )
        self.loadCombo(
            self.databasesCb, 
            [ 
                {'value': d['nome'], 'id': d['id']}
                for d in self.controller.getSapDatabases()
            ]
        )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "generatesWorkUnit.ui"
        )

    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('', '')
        for row in data:
            combo.addItem(row['value'], row['id'])

    def getData(self):
        crsid = self.comboBoxProjection.crs().authid().split(':')[-1] if self.comboBoxProjection.crs() else ''
        layerName = self.comboBoxPolygonLayer.currentLayer().name() if self.comboBoxPolygonLayer.currentLayer() else ''
        return {
            'layerName' : layerName,
            'xSize' : self.xSizeLe.value(),
            'ySize' : self.ySizeLe.value(),
            'overlap' : self.overlapLe.value(),
            'deplace' : self.deplaceLe.value(),
            'onlySelected' : self.onlySelectedCkb.isChecked(),
            'epsg': crsid,
            'bloco_id': self.blocksCb.itemData(self.blocksCb.currentIndex()),
            'dado_producao_id': self.databasesCb.itemData(self.databasesCb.currentIndex())
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        inputData = self.getData()
        try:
            self.qgis.generateWorkUnit(
                inputData['layerName'],
                (inputData['xSize'], inputData['ySize']),
                inputData['overlap'],
                inputData['deplace'],
                inputData['onlySelected'],
                inputData['epsg'],
                inputData['bloco_id'],
                inputData['dado_producao_id']
                
            )
            self.showInfo('Aviso', 'Unidades de trabalho geradas com sucesso!')
        except Exception as e:
            self.showError('Aviso', str(e))
