from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore

from Ferramentas_Gerencia.qgis.interfaces.IMapFunctions import IMapFunctions

class FillGeometries(IMapFunctions):

    def __init__(self):
        super(FillGeometries, self).__init__()

    def run(self):
        pass

    def fillGeometries(self, geoms, unionGeom, unionTranslatedGeom, deplace):
        diff = unionGeom.difference(unionTranslatedGeom)
        temp = []
        to_return = []
        # Complementing the upper part
        for geom in geoms:
            geom.translate(dx=deplace, dy=0)
            value = geom.intersection(diff)
            if value.wkbType() == QgsWkbTypes.Polygon:
                temp.append(value)
        complUnionX = QgsGeometry.unaryUnion(temp)
        # Complementing the left part
        for geom in geoms:
            geom.translate(dx=-deplace, dy=-deplace)
            value = geom.intersection(diff)
            if value.wkbType() == QgsWkbTypes.Polygon:
                temp.append(value.difference(complUnionX))
        complUnion = QgsGeometry.unaryUnion([*temp, unionTranslatedGeom])
        # Complementing the upper and left corner
        for geom in geoms:
            geom.translate(dx=0, dy=deplace)
            temp.append(geom.difference(complUnion))
        #Buffering and cleaning
        for geom in temp:
            if geom.wkbType() == QgsWkbTypes.MultiPolygon:
                collection = geom.asGeometryCollection()
                for part in collection:
                    if part.area() > 0.001 and part.wkbType() == QgsWkbTypes.Polygon:
                        buffered = self.buffer(part)
                        to_return.append(buffered.intersection(unionGeom))
            if geom.area() > 0.001 and geom.wkbType() == QgsWkbTypes.Polygon:
                buffered = self.buffer(geom)
                to_return.append(buffered.intersection(unionGeom))
        return to_return