from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore

from Ferramentas_Gerencia.qgis.interfaces.IMapFunctions import IMapFunctions

class ClipFeature(IMapFunctions):

    def __init__(self):
        super(ClipFeature, self).__init__()

    def run(self):
        pass

    def clipFeatures(self, geom):
        '''
        Gets an geometry, clips it using self.n_div and returns a list of clipped geometries
        '''
        clippedGeoms = []
        bbox = geom.boundingBox()
        x_max = bbox.xMaximum()
        x_min = bbox.xMinimum()
        y_max = bbox.yMaximum()
        y_min = bbox.yMinimum()
        for x in range(self.n_div):
            for y in range(self.n_div):
                length_x = x_max - x_min
                length_y = y_max - y_min
                new_geom = QgsGeometry.fromRect(QgsRectangle( x_min + x*(length_x)/self.n_div, y_min + y*(length_y)/self.n_div , x_min + (x+1)*(length_x)/self.n_div, y_min + (y+1)*(length_y)/self.n_div))
                clippedGeoms.append(new_geom)
        return clippedGeoms