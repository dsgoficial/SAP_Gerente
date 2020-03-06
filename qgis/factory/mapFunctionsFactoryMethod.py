from Ferramentas_Gerencia.qgis.mapFunctions.clipFeature  import ClipFeature
from Ferramentas_Gerencia.qgis.mapFunctions.fillGeometries  import FillGeometries

class MapFunctionsFactoryMethod:

    @staticmethod
    def getMapFunctions(functionName):
        if functionName == 'clipFeature':
            return ClipFeature()
        elif functionName == 'fillGeometries':
            return FillGeometries()
       