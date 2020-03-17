from Ferramentas_Gerencia.qgis.mapFunctions.buildGrid  import BuildGrid
from Ferramentas_Gerencia.qgis.mapFunctions.transformGeometryCrs  import TransformGeometryCrs
from Ferramentas_Gerencia.qgis.mapFunctions.createTemporaryLayer  import CreateTemporaryLayer
from Ferramentas_Gerencia.qgis.mapFunctions.unionGeometries  import UnionGeometries
from Ferramentas_Gerencia.qgis.mapFunctions.deagregator  import Deagregator
from Ferramentas_Gerencia.qgis.mapFunctions.generateUT  import GenerateUT

class MapFunctionsFactoryMethod:

    @staticmethod
    def getMapFunctions(functionName):
        if functionName == 'buildGrid':
            return BuildGrid()
        elif functionName == 'createTemporaryLayer':
            return CreateTemporaryLayer()
        elif functionName == 'transformGeometryCrs':
            return TransformGeometryCrs()
        elif functionName == 'unionGeometries':
            return UnionGeometries()
        elif functionName == 'generateUT':
            return GenerateUT()
        elif functionName == 'deagregator':
            return Deagregator()

       