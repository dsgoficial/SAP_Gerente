from PyQt5 import QtGui, QtCore
from qgis.utils import iface
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField
from qgis.PyQt.QtCore import QVariant
import math
from Ferramentas_Gerencia.modules.dsgTools.processingLaunchers.generateSystematicGridRelatedToLayer import GenerateSystematicGridRelatedToLayer

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
        result = self.generateSystematicGridRelatedToLayer.run(data)
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
        self.layersApi.addLayerOnMap(layer)
        return layer

    def addFields(self, layer, fields):
        provider = layer.dataProvider()
        provider.addAttributes([QgsField(name, QtCore.QVariant.String) for name in fields])
        layer.updateFields()