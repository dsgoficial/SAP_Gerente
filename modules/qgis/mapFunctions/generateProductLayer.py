from PyQt5 import QtGui, QtCore
from qgis.utils import iface
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField
from qgis.PyQt.QtCore import QVariant
import math
from SAP_Gerente.modules.dsgTools.processingLaunchers.generateSystematicGridRelatedToLayer import GenerateSystematicGridRelatedToLayer
import uuid

class GenerateProductLayer:

    def __init__(self,
            createTemporaryLayerFunction,
            layersApi,
            generateSystematicGridRelatedToLayer=GenerateSystematicGridRelatedToLayer()
        ):
        super(GenerateProductLayer, self).__init__()
        self.layersApi = layersApi
        self.createTemporaryLayerFunction = createTemporaryLayerFunction
        self.generateSystematicGridRelatedToLayer = generateSystematicGridRelatedToLayer

    def run(self, data):
        result = self.generateSystematicGridRelatedToLayer.run({
            'layerId': data['layerId'],
            'scale': data['scale']
        })
        layer = result['OUTPUT']
        self.addFields(
            layer,
            [
                'uuid',
                'nome',
                'denominador_escala',
                'edicao'
            ]
        )
        layerMap = self.layersApi.addLayerOnMap(layer)
        self.setDefaultFields(layerMap, data['scale'], data['edition'])
        return layer

    def addFields(self, layer, fields):
        provider = layer.dataProvider()
        provider.addAttributes([QgsField(name, QtCore.QVariant.String) for name in fields])
        layer.updateFields()

    def getScaleByIndex(self, idx):
        return [
            "1000000",
            "500000",
            "250000",
            "100000",
            "50000",
            "25000",
            "10000",
            "5000",
            "2000",
            "1000",
        ][idx]

    def setDefaultFields(self, layer, scaleIdx, edition):
        layer.startEditing()
        for f in layer.getFeatures():
            f['nome'] = f['mi']
            f['uuid'] = str(uuid.uuid4())
            f['denominador_escala'] = self.getScaleByIndex(scaleIdx)
            f['edicao'] = edition
            layer.updateFeature(f)
        layer.commitChanges()