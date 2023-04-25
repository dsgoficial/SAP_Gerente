from qgis import core, gui
from qgis.utils import iface
import processing

class Processing:
    
    def __init__(self):
        super(Processing, self).__init__()

    def getLayerUriFromId(self, layerId):
        loadedLayers = core.QgsProject.instance().mapLayers()
        if not(layerId in loadedLayers):
            return
        return loadedLayers[layerId].source()
           

    def getLayerUriFromTable(self, layerSchema, layerName):
        layersUri = []
        loadedLayers = core.QgsProject.instance().mapLayers().values()
        for layer in loadedLayers:
            if not(
                    layer.dataProvider().uri().schema() == layerSchema
                    and
                    layer.dataProvider().uri().table() == layerName
                ):
                continue
            return layer.source()

    def isAvailable(self):
        for alg in core.QgsApplication.processingRegistry().algorithms():
            if alg.id() == self.processingId:
                return True
        return False

    def run(self, parameters):
        if not self.isAvailable():
            raise Exception("Processamento '{0}' não está disponível".format(self.processingId))
            return
        return processing.run( self.processingId, self.getParameters(parameters) )

    def getParameters(self, parameters):
        raise NotImplementedError('Abstract Method')