from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore

from Ferramentas_Gerencia.qgis.interfaces.IMapFunctions import IMapFunctions

class CreateTemporaryLayer(IMapFunctions):

    def __init__(self):
        super(CreateTemporaryLayer, self).__init__()
        self.crs = ''

    def setCrs(self, crs):
        self.crs = crs

    def getCrs(self, crs):
        return self.crs

    def run(self):
        temp_layer_uri = 'Polygon?crs={}'.format(self.getCrs())
        temp_layer = QgsVectorLayer(temp_layer_uri, 'Teste', 'memory')
        temp_layer.setCrs(crs)