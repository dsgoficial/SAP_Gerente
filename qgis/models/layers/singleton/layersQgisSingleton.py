from Ferramentas_Gerencia.qgis.models.layers.layersQgis import LayersQgis

class LayersQgisSingleton:
    
    layersQgis = None

    @staticmethod
    def getInstance():
        if not LayersQgisSingleton.layersQgis:
            LayersQgisSingleton.layersQgis = LayersQgis()
        return LayersQgisSingleton.layersQgis