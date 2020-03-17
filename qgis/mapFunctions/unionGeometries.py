from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField

from Ferramentas_Gerencia.qgis.interfaces.IMapFunctions import IMapFunctions

class UnionGeometries(IMapFunctions):

    def __init__(self):
        super(UnionGeometries, self).__init__()

    def run(self, geometries):
        return QgsGeometry.unaryUnion(geometries)