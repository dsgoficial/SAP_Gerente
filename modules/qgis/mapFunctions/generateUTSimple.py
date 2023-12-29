from PyQt5 import QtGui, QtCore
from qgis.utils import iface
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField
from qgis.PyQt.QtCore import QVariant
import math

class GenerateUTSimple:

    def __init__(self,
            createTemporaryLayerFunction,
            transformGeometryCrsFunction,
            unionGeometriesFunction,
            deagregatorFunction,
            buildGridFunction,
            layersApi
        ):
        super(GenerateUTSimple, self).__init__()
        self.layersApi = layersApi
        self.createTemporaryLayerFunction = createTemporaryLayerFunction
        self.transformGeometryCrsFunction = transformGeometryCrsFunction
        self.unionGeometriesFunction = unionGeometriesFunction
        self.deagregatorFunction = deagregatorFunction
        self.buildGridFunction = buildGridFunction

    def run(
            self,
            layer,
            epsg,
            blockId,
            productionDataId,
            onlySelected
        ):
        self.validateParameter(layer.name(), onlySelected)
        features = self.layersApi.getActiveLayerSelections() if onlySelected else self.layersApi.getActiveLayerAllFeatures()
        crsSourceId = self.layersApi.getCrsId()
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
        for f in features:
            if f.geometry().isEmpty():
                continue
            self.layersApi.addFeature(
                temporaryLayer, 
                {
                    'nome': f['priority'],
                    'disponivel': True,
                    'dificuldade': 0,
                    'prioridade': f['priority'],
                    'epsg': epsg,
                    'bloco_id': blockId,
                    'dado_producao_id': productionDataId,
                    'tempo_estimado_minutos': 0
                }, 
                f.geometry()
            )
        self.layersApi.addLayerOnMap(temporaryLayer)
        return temporaryLayer
    
    def validateParameter(self, layerName, onlySelected):
        if not self.layersApi.isActiveLayer(layerName):
            raise Exception("Camada '{0}' não está selecionado!".format(layerName))
        if onlySelected and not self.layersApi.getActiveLayerSelections():
            raise Exception("Não há feições selecionadas.")