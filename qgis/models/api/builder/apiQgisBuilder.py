from PyQt5 import QtCore

from Ferramentas_Gerencia.qgis.models.api.interface.apiGisBuilderInterface import ApiGisBuilderInterface
from Ferramentas_Gerencia.qgis.models.api.apiQgis import ApiQgis

class ApiQgisBuilder(ApiGisBuilderInterface):

    def __init__(self):
        super(ApiQgisBuilder, self).__init__()
        self.apiQgis = ApiQgis()

    def setStyles(self, styles):
        self.apiQgis.setStyles(styles)

    def setLayers(self, layers):
        self.apiQgis.setLayers(layers)

    def setStorages(self, storages):
        self.apiQgis.setStorages(storages)

    def getResult(self):
        return self.apiQgis