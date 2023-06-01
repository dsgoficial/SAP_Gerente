from PyQt5 import QtGui, QtCore
from qgis.utils import iface
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField
from qgis.PyQt.QtCore import QVariant
import math

class GenerateMetadataLayer:

    def __init__(self,
            createTemporaryLayerFunction,
            layersApi
        ):
        super(GenerateMetadataLayer, self).__init__()
        self.layersApi = layersApi
        self.createTemporaryLayerFunction = createTemporaryLayerFunction

    def run(self):
        crsSourceId = self.layersApi.getMapCrsId()
        temporaryLayer = self.createTemporaryLayerFunction.run(
            'metadado', 
            'polygon', 
            [
                'nome',
                'epsg',
                'caminho'
            ], 
            crsSourceId
        )
        self.layersApi.addLayerOnMap(temporaryLayer)
        return temporaryLayer