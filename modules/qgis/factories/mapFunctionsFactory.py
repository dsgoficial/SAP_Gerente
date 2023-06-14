from Ferramentas_Gerencia.modules.qgis.mapFunctions.buildGrid  import BuildGrid
from Ferramentas_Gerencia.modules.qgis.mapFunctions.transformGeometryCrs  import TransformGeometryCrs
from Ferramentas_Gerencia.modules.qgis.mapFunctions.createTemporaryLayer  import CreateTemporaryLayer
from Ferramentas_Gerencia.modules.qgis.mapFunctions.unionGeometries  import UnionGeometries
from Ferramentas_Gerencia.modules.qgis.mapFunctions.deagregator  import Deagregator
from Ferramentas_Gerencia.modules.qgis.mapFunctions.generateUT  import GenerateUT
from Ferramentas_Gerencia.modules.qgis.mapFunctions.dumpFeatures  import DumpFeatures
from Ferramentas_Gerencia.modules.qgis.mapFunctions.geometryToEwkt  import GeometryToEwkt
from Ferramentas_Gerencia.modules.qgis.mapFunctions.createNewMapView  import CreateNewMapView
from Ferramentas_Gerencia.modules.qgis.factories.qgisApiSingleton import QgisApiSingleton
from Ferramentas_Gerencia.modules.qgis.mapFunctions.generateUTSimple  import GenerateUTSimple
from Ferramentas_Gerencia.modules.qgis.mapFunctions.generateMetadataLayer  import GenerateMetadataLayer
from Ferramentas_Gerencia.modules.qgis.mapFunctions.generateProductLayer  import GenerateProductLayer

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

    def createGenerateUTSimple(self):
        return GenerateUTSimple(
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

    def createGenerateMetadataLayer(self):
        return GenerateMetadataLayer(
            createTemporaryLayerFunction=self.getMapFunction('createTemporaryLayer'),
            layersApi=QgisApiSingleton.getInstance()
        )

    def createGenerateProductLayer(self):
        return GenerateProductLayer(
            createTemporaryLayerFunction=self.getMapFunction('createTemporaryLayer'),
            layersApi=QgisApiSingleton.getInstance()
        )

    def getMapFunction(self, functionName):
        functionNames = {
            'buildGrid': BuildGrid,
            'createTemporaryLayer': CreateTemporaryLayer,
            'transformGeometryCrs': TransformGeometryCrs,
            'unionGeometries': UnionGeometries,
            'generateUT': self.createGenerateUT,
            'deagregator': Deagregator,
            'createNewMapView': CreateNewMapView,
            'dumpFeatures': DumpFeatures,
            'geometryToEwkt': self.createGeometryToEwkt,
            'generateUTSimple': self.createGenerateUTSimple,
            'generateMetadataLayer': self.createGenerateMetadataLayer,
            'generateProductLayer': self.createGenerateProductLayer
        }
        return functionNames[functionName]()