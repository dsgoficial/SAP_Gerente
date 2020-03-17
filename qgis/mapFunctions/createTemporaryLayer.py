from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField

from Ferramentas_Gerencia.qgis.interfaces.IMapFunctions import IMapFunctions

class CreateTemporaryLayer(IMapFunctions):

    def __init__(self):
        super(CreateTemporaryLayer, self).__init__()

    def run(self, layerName, geometryType, fields, crs):
        if geometryType == 'polygon':
            layer = self.buildPolygon(layerName, crs) 
        self.addFields(layer, fields)
        return layer

    def addFields(self, layer, fields):
        provider = layer.dataProvider()
        provider.addAttributes([QgsField(name, QtCore.QVariant.String) for name in fields])
        layer.updateFields()

    def buildPolygon(self, layerName, crs):
        temp_layer_uri = 'Polygon?crs={}'.format(crs)
        temp_layer = QgsVectorLayer(temp_layer_uri, layerName, 'memory')
        temp_layer.setCrs(QgsCoordinateReferenceSystem(crs))
        return temp_layer