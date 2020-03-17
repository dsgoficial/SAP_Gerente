from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore
from qgis.core import QgsGeometry, QgsRectangle
from qgis.PyQt.QtCore import QVariant
import math

from Ferramentas_Gerencia.qgis.interfaces.IMapFunctions import IMapFunctions

class BuildGrid(IMapFunctions):

    def __init__(self):
        super(BuildGrid, self).__init__()

    def run(self, unionGeom, size):
        xSize = size[0]
        ySize = size[1]
        grid = []
        bbox = unionGeom.boundingBox()
        x_max = bbox.xMaximum()
        x_min = bbox.xMinimum()
        y_max = bbox.yMaximum()
        y_min = bbox.yMinimum()
        print(xSize, ySize)
        print(x_max, x_min)
        div_x = math.ceil((x_max - x_min)/xSize)
        div_y = math.ceil((y_max - y_min)/ySize)
        for x in range(-1, div_x):
            for y in range(-1, div_y):
                new_geom = QgsGeometry.fromRect(QgsRectangle( x_min + x*xSize, y_max - y*ySize , x_min + (x+1)*xSize, y_max - (y+1)*ySize))
                grid.append(new_geom)
        return grid