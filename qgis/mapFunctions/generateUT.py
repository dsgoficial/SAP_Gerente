from PyQt5 import QtGui, QtCore
from qgis.utils import iface
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField
from qgis.PyQt.QtCore import QVariant
import math

from Ferramentas_Gerencia.qgis.interfaces.IMapFunctions import IMapFunctions

class GenerateUT(IMapFunctions):

    def __init__(self):
        super(GenerateUT, self).__init__()

    def validateParameter(self, layerName, onlySelected, deplace, layersApi):
        if not layersApi.isActiveLayer(layerName):
            raise Exception("Camada '{0}' não está selecionado!".format(layerName))
        if onlySelected and not layersApi.getActiveLayerSelections():
            raise Exception("Não há feições selecionadas.")
        if deplace < 0:
            raise Exception("Valor de deslocamento inválido")
        if not layersApi.isPolygon():
            raise Exception("A geometria inserida não é do tipo polígono.")

    def run(self,
            layerName,
            size,
            prefixName,
            overlay, 
            deplace,
            onlySelected,
            layersApi,
            createTemporaryLayerFunction,
            transformGeometryCrsFunction,
            unionGeometriesFunction,
            deagregatorFunction,
            buildGridFunction
        ):
        self.validateParameter(layerName, onlySelected, deplace, layersApi)
        features = layersApi.getActiveLayerSelections() if onlySelected else layersApi.getActiveLayerAllFeatures()
        geometries = [ f.geometry() for f in features]
        crsSourceId = layersApi.getCrsId()
        crsDestId = "EPSG:3857"
        transformedGeometries = transformGeometryCrsFunction.run(geometries, crsSourceId, crsDestId)
        unionGeom = unionGeometriesFunction.run(transformedGeometries)
        grid = buildGridFunction.run(unionGeom, size)
        temporaryLayer = createTemporaryLayerFunction.run('generateUT', 'polygon', ['name'], crsSourceId)
        idx = 0
        for geom in grid:
            geom.translate(dx=deplace, dy=-deplace)
            geom_temp = geom.intersection(unionGeom)
            buffered = geom_temp.buffer(overlay, segments=10)
            workUnitGeom = buffered.intersection(unionGeom)
            transWorkUnitGeom = transformGeometryCrsFunction.run([workUnitGeom], crsDestId, crsSourceId)
            for geom in deagregatorFunction.run(transWorkUnitGeom):
                layersApi.addFeature(temporaryLayer, {'name': '{}_{}'.format(prefixName, idx)}, geom)
                idx +=1
        layersApi.addLayerOnMap(temporaryLayer)



    

    """ def run2(self, geom, unionGeom, deplace, overlay ):
        geom.translate(dx=deplace, dy=-deplace)
        geom_temp = geom.intersection(unionGeom)
        buffered = geom_temp.buffer(overlay, segments=10)
        return buffered.intersection(unionGeom) """

    """ features = layersApi.getActiveLayerSelections() if onlySelected else layersApi.getActiveLayerAllFeatures()
    geometries = [ f.geometry() for f in features]
    crsSourceId = layersApi.getCrsId()
    crsDestId = "EPSG:3857"

    createTemporaryLayer = MapFunctionsFactoryMethod.getMapFunctions('createTemporaryLayer')
    transformGeometryCrs = MapFunctionsFactoryMethod.getMapFunctions('transformGeometryCrs')
    unionGeometries = MapFunctionsFactoryMethod.getMapFunctions('unionGeometries')
    deagregator = MapFunctionsFactoryMethod.getMapFunctions('deagregator')
    generateUT = MapFunctionsFactoryMethod.getMapFunctions('generateUT')
    buildGrid = MapFunctionsFactoryMethod.getMapFunctions('buildGrid')
    
    transformedGeometries = transformGeometryCrs.run(geometries, crsSourceId, crsDestId)
    unionGeom = unionGeometries.run(transformedGeometries)
    grid = buildGrid.run(unionGeom, size)
    temporaryLayer = createTemporaryLayer.run('generateUT', 'polygon', ['name'], crsFrom)
    
    idx = 0
    for geom in grid:
        workUnitGeom = generateUT.run(geom, unionGeom, deplace, overlay)
        transWorkUnitGeom = transformGeometryCrs.run(workUnitGeom, crsDestId, crsSourceId)
        for geom in deagregator.run(transWorkUnitGeom):
            layersApi.addFeature(temporaryLayer, {'name': '{}_{}'.format(prefixName, idx)}, geom)
            idx +=1
    layersApi.addLayerOnMap(temporaryLayer) """

            