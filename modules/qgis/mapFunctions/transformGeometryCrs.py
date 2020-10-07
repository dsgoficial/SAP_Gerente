from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField
from qgis.PyQt.QtCore import QVariant
import math

from Ferramentas_Gerencia.modules.qgis.interfaces.IMapFunction import IMapFunction

class TransformGeometryCrs(IMapFunction):

    def __init__(self):
        super(TransformGeometryCrs, self).__init__()

    def run(self, geometries, crsFrom, crsTo):
        if crsFrom == crsTo:
            return geometries
        newCrs = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem(crsFrom), 
            QgsCoordinateReferenceSystem(crsTo), 
            QgsProject.instance()
        )
        if type(geometries) == list:
            newGeometries = []      
            for geom in geometries:
                geom.transform(newCrs)
                newGeometries.append(geom)
            return newGeometries
        geometries.transform(newCrs)
        return geometries