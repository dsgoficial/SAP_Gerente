from Ferramentas_Gerencia.qgis.factory.storagesSingleton import StoragesSingleton
from Ferramentas_Gerencia.qgis.factory.layersSingleton import LayersSingleton
from Ferramentas_Gerencia.qgis.factory.stylesSingleton import StylesSingleton

class QgisApiDirector:

    #interface
    def constructQgisApi(self, qgisApiBuilder):
        qgisApiBuilder.setStyles(
            StylesSingleton.getInstance()
        )
        qgisApiBuilder.setLayers(
            LayersSingleton.getInstance()
        )
        qgisApiBuilder.setStorages(
            StoragesSingleton.getInstance()
        )