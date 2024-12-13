import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from .inputDialogV2  import InputDialogV2 

class GeneratesWorkUnitSimple(InputDialogV2):

    def __init__(
            self, 
            comboBoxPolygonLayer,
            comboBoxProjection, 
            controller,
            sap,
            qgis
        ):
        super(GeneratesWorkUnitSimple, self).__init__(controller=controller)
        self.sap = sap
        self.qgis = qgis
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        self.comboBoxProjection = comboBoxProjection
        self.comboBoxProjection.setFixedSize(QtCore.QSize(250, 25))
        self.epsgLayout.addWidget(self.comboBoxProjection)
        self.overlapLe.setText('0.0')
        self.setWindowTitle('Gerar Unidades de Trabalho')
        self.loadCombo(
            self.blocksCb, 
            [ {'value': '', 'id': ''}]
            + 
            [ 
                {'value': d['nome'], 'id': d['id']}
                for d in self.sap.getBlocks()
            ]
        )
        self.loadCombo(
            self.databasesCb,
            [ {'value': '', 'id': ''}]
            + 
            [ 
                {'value': d['nome'], 'id': d['id']}
                for d in self.controller.getSapDatabases()
                if d['lote_status_id'] == 1
            ]
        )
        
        self.loadCombo(
            self.splitFactorsCb, 
            [ 
                {'value': '...', 'id': None},
                {'value': '1/1', 'id': 0},
                {'value': '1/4', 'id': 1},
                {'value': '1/9', 'id': 2},
                {'value': '1/16', 'id': 3},
                {'value': '1/25', 'id': 4}
            ]
        )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "generatesWorkUnitSimple.ui"
        )

    def loadCombo(self, combo, data):
        combo.clear()
        for row in data:
            combo.addItem(row['value'], row['id'])

    def getData(self):
        crsid = self.comboBoxProjection.crs().authid().split(':')[-1] if self.comboBoxProjection.crs() else ''
        layer = self.comboBoxPolygonLayer.currentLayer() if self.comboBoxPolygonLayer.currentLayer() else ''
        return {
            'layerId': layer.id() if layer else '',
            'layer': layer,
            'overlap' : float(self.overlapLe.text()),
            'epsg': crsid,
            'bloco_id': self.blocksCb.itemData(self.blocksCb.currentIndex()),
            'dado_producao_id': self.databasesCb.itemData(self.databasesCb.currentIndex()),
            'param': self.splitFactorsCb.itemData(self.splitFactorsCb.currentIndex()),
            'onlySelected': self.onlySelectedCkb.isChecked()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        
        #try:
            data = self.getData()
            self.controller.createWorkUnitSimple(data)
            self.showInfo('Aviso', 'Unidades de trabalho geradas com sucesso!')
        #except Exception as e:
        #    self.showError('Aviso', str(e))
