from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore
from qgis.core import QgsGeometry
from qgis.PyQt.QtCore import QVariant
import math

from SAP_Gerente.modules.qgis.interfaces.IMapFunction import IMapFunction

class Deagregator(IMapFunction):

    def __init__(self):
        super(Deagregator, self).__init__()

    def run(self, geometries):
        deagregatorGeometries = []
        for geometry in geometries:
            if not geometry.isMultipart():
                deagregatorGeometries.append(geometry)
                continue
            collection = geometry.asGeometryCollection()
            for part in collection:
                deagregatorGeometries.append(part)
        return deagregatorGeometries