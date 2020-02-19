from Ferramentas_Gerencia.qgis.layers.layers import Layers

class LayersSingleton:
    
    layers = None

    @staticmethod
    def getInstance():
        if not LayersSingleton.layers:
            LayersSingleton.layers = Layers()
        return LayersSingleton.layers