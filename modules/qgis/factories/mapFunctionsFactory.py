from Ferramentas_Gerencia.modules.qgis.mapFunctions.buildGrid  import BuildGrid
from Ferramentas_Gerencia.modules.qgis.mapFunctions.transformGeometryCrs  import TransformGeometryCrs
from Ferramentas_Gerencia.modules.qgis.mapFunctions.createTemporaryLayer  import CreateTemporaryLayer
from Ferramentas_Gerencia.modules.qgis.mapFunctions.unionGeometries  import UnionGeometries
from Ferramentas_Gerencia.modules.qgis.mapFunctions.deagregator  import Deagregator
from Ferramentas_Gerencia.modules.qgis.mapFunctions.generateUT  import GenerateUT
from Ferramentas_Gerencia.modules.qgis.mapFunctions.dumpFeatures  import DumpFeatures
from Ferramentas_Gerencia.modules.qgis.mapFunctions.geometryToEwkt  import GeometryToEwkt

from Ferramentas_Gerencia.modules.qgis.factories.qgisApiSingleton import QgisApiSingleton

class MapFunctionsFactory:

    def createGenerateUT(self):
        return GenerateUT(
            createTemporaryLayerFunction=self.getMapFunction('createTemporaryLayer'),
            transformGeometryCrsFunction=self.getMapFunction('transformGeometryCrs'),
            unionGeometriesFunction=self.getMapFunction('unionGeometries'),
            deagregatorFunction=self.getMapFunction('deagregator'),
            buildGridFunction=self.getMapFunction('buildGrid'),
            layersApi=QgisApiSingleton.getInstance()
        )

    def createGeometryToEwkt(self):
        return GeometryToEwkt(
            transformGeometryCrsFunction=self.getMapFunction('transformGeometryCrs')
        )

    def getMapFunction(self, functionName):
        functionNames = {
            'buildGrid': BuildGrid,
            'createTemporaryLayer': CreateTemporaryLayer,
            'transformGeometryCrs': TransformGeometryCrs,
            'unionGeometries': UnionGeometries,
            'generateUT': self.createGenerateUT,
            'deagregator': Deagregator,
            'dumpFeatures': DumpFeatures,
            'geometryToEwkt': self.createGeometryToEwkt,
        }
        return functionNames[functionName]()