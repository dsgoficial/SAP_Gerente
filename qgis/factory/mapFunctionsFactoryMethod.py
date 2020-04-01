from Ferramentas_Gerencia.qgis.mapFunctions.buildGrid  import BuildGrid
from Ferramentas_Gerencia.qgis.mapFunctions.transformGeometryCrs  import TransformGeometryCrs
from Ferramentas_Gerencia.qgis.mapFunctions.createTemporaryLayer  import CreateTemporaryLayer
from Ferramentas_Gerencia.qgis.mapFunctions.unionGeometries  import UnionGeometries
from Ferramentas_Gerencia.qgis.mapFunctions.deagregator  import Deagregator
from Ferramentas_Gerencia.qgis.mapFunctions.generateUT  import GenerateUT
from Ferramentas_Gerencia.qgis.mapFunctions.dumpFeatures  import DumpFeatures
from Ferramentas_Gerencia.qgis.mapFunctions.geometryToEwkt  import GeometryToEwkt

from Ferramentas_Gerencia.qgis.factory.qgisApiSingleton import QgisApiSingleton

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
            return GenerateUT(
                    createTemporaryLayerFunction=MapFunctionsFactoryMethod.getMapFunctions('createTemporaryLayer'),
                    transformGeometryCrsFunction=MapFunctionsFactoryMethod.getMapFunctions('transformGeometryCrs'),
                    unionGeometriesFunction=MapFunctionsFactoryMethod.getMapFunctions('unionGeometries'),
                    deagregatorFunction=MapFunctionsFactoryMethod.getMapFunctions('deagregator'),
                    buildGridFunction=MapFunctionsFactoryMethod.getMapFunctions('buildGrid'),
                    layersApi=QgisApiSingleton.getInstance().getLayers()
                )
        elif functionName == 'deagregator':
            return Deagregator()
        elif functionName == 'dumpFeatures':
            return DumpFeatures()
        elif functionName == 'geometryToEwkt':
            return GeometryToEwkt(
                transformGeometryCrsFunction=MapFunctionsFactoryMethod.getMapFunctions('transformGeometryCrs')
            )