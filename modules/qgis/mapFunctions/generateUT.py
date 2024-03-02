from PyQt5 import QtGui, QtCore
from qgis.utils import iface
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField
from qgis.PyQt.QtCore import QVariant
import math

from SAP_Gerente.modules.qgis.interfaces.IMapFunction import IMapFunction

class GenerateUT(IMapFunction):

    def __init__(self,
            createTemporaryLayerFunction,
            transformGeometryCrsFunction,
            unionGeometriesFunction,
            deagregatorFunction,
            buildGridFunction,
            layersApi
        ):
        super(GenerateUT, self).__init__()
        self.layersApi = layersApi
        self.createTemporaryLayerFunction = createTemporaryLayerFunction
        self.transformGeometryCrsFunction = transformGeometryCrsFunction
        self.unionGeometriesFunction = unionGeometriesFunction
        self.deagregatorFunction = deagregatorFunction
        self.buildGridFunction = buildGridFunction

    def validateParameter(self, layerName, onlySelected, deplace):
        if not self.layersApi.isActiveLayer(layerName):
            raise Exception("Camada '{0}' não está selecionado!".format(layerName))
        if onlySelected and not self.layersApi.getActiveLayerSelections():
            raise Exception("Não há feições selecionadas.")
        if deplace < 0:
            raise Exception("Valor de deslocamento inválido")
        if not self.layersApi.isPolygon():
            raise Exception("A geometria inserida não é do tipo polígono.")

    def run(
            self,
            layerName,
            size,
            overlay, 
            deplace,
            onlySelected,
            epsg,
            blockId,
            productionDataId
        ):
        self.validateParameter(layerName, onlySelected, deplace)
        features = self.layersApi.getActiveLayerSelections() if onlySelected else self.layersApi.getActiveLayerAllFeatures()
        geometries = [ f.geometry() for f in features]
        crsSourceId = self.layersApi.getCrsId()
        crsDestId = "EPSG:3857"
        transformedGeometries = self.transformGeometryCrsFunction.run(geometries, crsSourceId, crsDestId)
        unionGeom = self.unionGeometriesFunction.run(transformedGeometries)
        grid = self.buildGridFunction.run(unionGeom, size)
        temporaryLayer = self.createTemporaryLayerFunction.run(
            'generateUT', 
            'polygon', 
            [
                'nome',
                'epsg',
                'observacao',
                'dado_producao_id',
                'bloco_id',
                'disponivel',
                'prioridade',
                'dificuldade',
                'epsg',
                'bloco_id',
                'dado_producao_id',
                'tempo_estimado_minutos'
            ], 
            crsSourceId
        )
        idx = 0
        for geom in grid:
            geom.translate(dx=deplace, dy=-deplace)
            geom_temp = geom.intersection(unionGeom)
            buffered = geom_temp.buffer(overlay, segments=10)
            workUnitGeom = buffered.intersection(unionGeom)
            transWorkUnitGeom = self.transformGeometryCrsFunction.run([workUnitGeom], crsDestId, crsSourceId)
            for geom in self.deagregatorFunction.run(transWorkUnitGeom):
                if geom.isEmpty():
                    continue
                self.layersApi.addFeature(
                    temporaryLayer, 
                    {
                        'nome': idx,
                        'disponivel': True,
                        'dificuldade': 0,
                        'prioridade': idx,
                        'epsg': epsg,
                        'bloco_id': blockId,
                        'dado_producao_id': productionDataId,
                        'tempo_estimado_minutos': 0
                    }, 
                    geom
                )
                idx +=1
        self.layersApi.addLayerOnMap(temporaryLayer)