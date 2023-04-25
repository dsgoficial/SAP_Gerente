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
            productionDataId
            
        ):
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
                'dado_producao_id'
            ], 
            crsSourceId
        )
        for f in layer.getFeatures():
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
                    'dado_producao_id': productionDataId
                }, 
                f.geometry()
            )
        self.layersApi.addLayerOnMap(temporaryLayer)
        return temporaryLayer