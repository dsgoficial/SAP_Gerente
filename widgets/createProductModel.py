import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2
from qgis import core
from functools import cmp_to_key

class CreateProductModel(InputDialogV2):

    create = QtCore.pyqtSignal(dict)

    def __init__(self, parent, comboBoxPolygonLayer, sapCtrl):
        super(CreateProductModel, self).__init__(parent=parent, controller=sapCtrl)
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        self.setWindowTitle('Gerar Modelo de Camada Produto')
        self.loadScales([
            {
                'nome': scale,
                'value': idx
            }
            for idx, scale in enumerate(self.getScales())
        ])

    def getScales(self):
        return [
            "1000k",
            "500k",
            "250k",
            "100k",
            "50k",
            "25k",
            "10k",
            "5k",
            "2k",
            "1k",
        ]

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createProductModel.ui"
        )

    def getScale(self):
        return self.scaleCb.itemData(self.scaleCb.currentIndex())

    def validInput(self):
        return (
            self.comboBoxPolygonLayer.currentLayer()
            and
            self.getScale() != None
        )

    def loadScales(self, data):
        self.scaleCb.clear()
        self.scaleCb.addItem('...', None)
        for row in data:
            self.scaleCb.addItem(
                row['nome'], 
                row['value']
            )       

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showInfo('Aviso', 'Preencha todos os campos!')
            return
        self.create.emit({
            'layerId': self.comboBoxPolygonLayer.currentLayer().id(),
            'scale': self.getScale(),
            'edition': self.editionLe.text()
        })
        self.showInfo('Aviso', 'Criado com sucesso!')
        self.close()