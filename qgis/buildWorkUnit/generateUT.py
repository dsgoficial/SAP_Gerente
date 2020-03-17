from qgis.utils import iface
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry, QgsField
from qgis.PyQt.QtCore import QVariant
import math

class GenerateDivisions():
    def __init__(self,layer, divisoes, sobreposicao, deslocamento, prefixo, apenas_selecionado):
        self.layer = layer
        [self.nx, self.ny] = divisoes
        self.overlay = sobreposicao
        self.deplace = deslocamento
        self.selected = bool(apenas_selecionado)
        self.prefix = prefixo
        
    def parameterValidation(self):
        if not self.layer:
            iface.messageBar().pushMessage(u'Erro', "Selecione o layer", level=Qgis.Critical)
            return False
        if self.deplace < 0:
            iface.messageBar().pushMessage(u'Erro', "Valor de deslocamento inválido", level=Qgis.Critical)
            return False
        if self.selected:
            features = self.layer.selectedFeatures()
            if not features:
                iface.messageBar().pushMessage(u'Erro', "Não há feições selecionadas.", level=Qgis.Critical)
                return False
        else:
            features = self.layer.getFeatures()
        for item in features:
            geom = item.geometry()
            if geom.wkbType() not in [3, 6]: # IDs for Polygon and MultiPolygon
                iface.messageBar().pushMessage(u'Erro', "A geometria inserida não é do tipo polígono.", level=Qgis.Critical)
                return False
        return True
        
    def createGrid(self, unionGeom):
        '''
        Gets an geometry, clips it using self.n_div and returns a list of clipped geometries
        '''
        grid = []
        bbox = unionGeom.boundingBox()
        x_max = bbox.xMaximum()
        x_min = bbox.xMinimum()
        y_max = bbox.yMaximum()
        y_min = bbox.yMinimum()
        
        div_x = math.ceil((x_max - x_min)/self.nx)
        div_y = math.ceil((y_max - y_min)/self.ny)
        for x in range(-1, div_x):
            for y in range(-1, div_y):
                new_geom = QgsGeometry.fromRect(QgsRectangle( x_min + x*self.nx, y_max - y*self.ny , x_min + (x+1)*self.nx, y_max - (y+1)*self.ny))
                #intersectGeom = new_geom.intersection(unionGeom)
                grid.append(new_geom)
        return grid
        
    def checkMultipart(self, geom):
        geomsToReturn = []
        if geom.isMultipart():
            collection = geom.asGeometryCollection()
            for part in collection:
                geomsToReturn.append(part)
            return geomsToReturn
        else:
            return [geom]

    def buffer(self, geom):
        return geom.buffer(self.overlay, segments=10)
        
    def runProcess(self):
        geoms = []

        """ if self.selected:
            features = self.layer.selectedFeatures()
        else:
            features = self.layer.getFeatures()
        crs = self.layer.crs()
        
        
        temp_layer_uri = 'Polygon?crs={}'.format(crs)
        temp_layer = QgsVectorLayer(temp_layer_uri, 'unidadesTrabalho', 'memory')
        temp_layer.setCrs(crs) """



        provider = temp_layer.dataProvider()
        # Creating name field
        provider.addAttributes([QgsField("name", QVariant.String)])
        temp_layer.updateFields()


       """  # Defining Coordinate Transformation
        tr_ida = QgsCoordinateTransform(crs, QgsCoordinateReferenceSystem("EPSG:3857"), QgsProject.instance())

        tr_volta = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:3857"), crs, QgsProject.instance())
        
        for feature in features:
            new_geom = feature.geometry()
            new_geom.transform(tr_ida)
            geoms.append(new_geom) """
        
        """ unionGeom = QgsGeometry.unaryUnion(geoms)
        
        grid = self.createGrid(unionGeom) """
        
        for geom in grid:
            geom.translate(dx=self.deplace, dy=-self.deplace)
            geom_temp = geom.intersection(unionGeom)
            buffered = self.buffer(geom_temp)
            geom2 = buffered.intersection(unionGeom)
            
            
            # Return to old projection and add on provider
            geom2.transform(tr_volta)
            for geomValid in self.checkMultipart(geom2):
                feat = QgsFeature()
                feat.setGeometry(geomValid)
                provider.addFeature(feat)



        for index, feat in enumerate(temp_layer.getFeatures()):
            name = '{}_{}'.format(self.prefix, index)
            temp_layer.startEditing()
            feat['name'] = name
            temp_layer.updateFeature(feat)
        temp_layer.commitChanges()
        QgsProject.instance().addMapLayer(temp_layer)
        
layer = iface.activeLayer()
# [tamanho_x, tamanho_y], sobreposicao, deslocamento, prefixo da feição, apenas_selecionado
generate = GenerateDivisions(layer, [5000, 8000], 200, 500,'Teste', False)
if generate.parameterValidation():
    generate.runProcess()

