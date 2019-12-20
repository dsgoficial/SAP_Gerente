from Ferramentas_Gerencia.qgis.models.storages.singleton.storagesQgisSingleton import StoragesQgisSingleton
from Ferramentas_Gerencia.qgis.models.layers.singleton.layersQgisSingleton import LayersQgisSingleton
from Ferramentas_Gerencia.qgis.models.styles.singleton.stylesQgisSingleton import StylesQgisSingleton

class ApiGisDirector:

    #interface
    def constructApiQgis(self, apiQgisBuilder):
        apiQgisBuilder.setStyles(
            StylesQgisSingleton.getInstance()
        )
        apiQgisBuilder.setLayers(
            LayersQgisSingleton.getInstance()
        )
        apiQgisBuilder.setStorages(
            StoragesQgisSingleton.getInstance()
        )