from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore
from qgis.core import QgsGeometry
from qgis.PyQt.QtCore import QVariant
import math

from SAP_Gerente.modules.qgis.interfaces.IMapFunction import IMapFunction

class DumpFeatures(IMapFunction):

    def __init__(self):
        super(DumpFeatures, self).__init__()

    def run(self, layer, onlySelected):
        features =  layer.selectedFeatures() if onlySelected else layer.getFeatures()
        featuresValues = []
        for feat in features:
            data = {}
            for field in layer.fields().names():
                data[field] = '' if str(feat[field]) == 'NULL' else feat[field]
            data['geometry'] = feat.geometry()
            featuresValues.append(data)
        return featuresValues