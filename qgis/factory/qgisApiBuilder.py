from PyQt5 import QtCore

from Ferramentas_Gerencia.qgis.interfaces.IQgisApiBuilder import IQgisApiBuilder
from Ferramentas_Gerencia.qgis.api.qgisApi import QgisApi

class QgisApiBuilder(IQgisApiBuilder):

    def __init__(self):
        super(QgisApiBuilder, self).__init__()
        self.qgisApi = QgisApi()

    def setStyles(self, styles):
        self.qgisApi.setStyles(styles)

    def setLayers(self, layers):
        self.qgisApi.setLayers(layers)

    def setStorages(self, storages):
        self.qgisApi.setStorages(storages)

    def getResult(self):
        return self.qgisApi