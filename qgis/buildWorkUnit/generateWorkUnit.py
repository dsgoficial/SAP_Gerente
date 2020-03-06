from qgis.utils import iface
from qgis.core import Qgis, QgsWkbTypes, QgsFeature, QgsVectorLayer, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry
import math

class GenerateDivisions():
    def __init__(self,layer, divisoes, sobreposicao, deslocamento, apenas_selecionado):
        self.layer = layer
        self.n_div = divisoes
        self.overlay = sobreposicao
        self.deplace = deslocamento
        self.selected = bool(apenas_selecionado)
        
    def parameterValidation(self):
        if not self.layer:
            iface.messageBar().pushMessage(u'Erro', "Selecione o layer", level=Qgis.Critical)
            return False
        if not 0.0 < self.deplace < 1.0:
            iface.messageBar().pushMessage(u'Erro', "Valor de deslocamento inválido (deve ser entre 0 e 1)", level=Qgis.Critical)
            return False
        if self.selected:
            features = self.layer.selectedFeatures()
        else:
            features = self.layer.getFeatures()
        for item in features:
            geom = item.geometry()
            if (geom.wkbType() != QgsWkbTypes.MultiPolygon and geom.wkbType() != QgsWkbTypes.Polygon):
                iface.messageBar().pushMessage(u'Erro', "A geometria inserida não é do tipo polígono.", level=Qgis.Critical)
                return False
        return True
    
    def clipFeatures(self, geom):
        '''
        Gets an geometry, clips it using self.n_div and returns a list of clipped geometries
        '''
        clippedGeoms = []
        bbox = geom.boundingBox()
        x_max = bbox.xMaximum()
        x_min = bbox.xMinimum()
        y_max = bbox.yMaximum()
        y_min = bbox.yMinimum()
        for x in range(self.n_div):
            for y in range(self.n_div):
                length_x = x_max - x_min
                length_y = y_max - y_min
                new_geom = QgsGeometry.fromRect(QgsRectangle( x_min + x*(length_x)/self.n_div, y_min + y*(length_y)/self.n_div , x_min + (x+1)*(length_x)/self.n_div, y_min + (y+1)*(length_y)/self.n_div))
                clippedGeoms.append(new_geom)
        return clippedGeoms
        
    def fillGeometries(self, geoms, unionGeom, unionTranslatedGeom, deplace):
        diff = unionGeom.difference(unionTranslatedGeom)
        temp = []
        to_return = []
        # Complementing the upper part
        for geom in geoms:
            geom.translate(dx=deplace, dy=0)
            value = geom.intersection(diff)
            if value.wkbType() == QgsWkbTypes.Polygon:
                temp.append(value)
        complUnionX = QgsGeometry.unaryUnion(temp)
        # Complementing the left part
        for geom in geoms:
            geom.translate(dx=-deplace, dy=-deplace)
            value = geom.intersection(diff)
            if value.wkbType() == QgsWkbTypes.Polygon:
                temp.append(value.difference(complUnionX))
        complUnion = QgsGeometry.unaryUnion([*temp, unionTranslatedGeom])
        # Complementing the upper and left corner
        for geom in geoms:
            geom.translate(dx=0, dy=deplace)
            temp.append(geom.difference(complUnion))
        #Buffering and cleaning
        for geom in temp:
            if geom.wkbType() == QgsWkbTypes.MultiPolygon:
                collection = geom.asGeometryCollection()
                for part in collection:
                    if part.area() > 0.001 and part.wkbType() == QgsWkbTypes.Polygon:
                        buffered = self.buffer(part)
                        to_return.append(buffered.intersection(unionGeom))
            if geom.area() > 0.001 and geom.wkbType() == QgsWkbTypes.Polygon:
                buffered = self.buffer(geom)
                to_return.append(buffered.intersection(unionGeom))
        return to_return
        
    def buffer(self, geom):
        return geom.buffer(self.overlay, segments=10)
        
    def calc_deplace(self, geom):
        bbox = geom.boundingBox()
        diagonal =  math.sqrt(math.pow((bbox.xMaximum() - bbox.xMinimum()), 2) + math.pow((bbox.yMaximum() - bbox.yMinimum()), 2))/self.n_div
        return self.deplace*diagonal
    
    def checkPolygonConsistency(self,geom):
        polygon = geom.asPolygon()[0]
        bbox = QgsGeometry.fromRect(geom.boundingBox())
        for point in polygon:
            _temp = QgsGeometry.fromPointXY(point)
            if _temp.within(bbox):
                return bbox
        
    def runProcess(self):
        geoms = []
        if self.selected:
            features = self.layer.selectedFeatures()
            _deplace_geom = features[0].geometry()
        else:
            features = self.layer.getFeatures()
            for feat in features:
                _deplace_geom = feat.geometry()
                break
                
        crs = self.layer.crs()
        temp_layer_uri = 'Polygon?crs={}'.format(crs)
        temp_layer = QgsVectorLayer(temp_layer_uri, 'Teste', 'memory')
        temp_layer.setCrs(crs)
        provider = temp_layer.dataProvider()


        
        tr_ida = QgsCoordinateTransform(crs, QgsCoordinateReferenceSystem("EPSG:3857"), QgsProject.instance())
        tr_volta = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:3857"), crs, QgsProject.instance())
        _deplace_geom.transform(tr_ida)

        deplace = self.calc_deplace(_deplace_geom)
        
        for feature in features:
            new_geom = feature.geometry()
            new_geom.transform(tr_ida)
            geoms.append(new_geom)
        
        unionGeom = QgsGeometry.unaryUnion(geoms)

        temp = []
        temp_geoms = []
        
        for new_geom in geoms:
            clipped = self.clipFeatures(new_geom)
            for geom in clipped:
                # Operations
                geom2 = geom.intersection(new_geom)
                # Append to get the union of geometries
                temp_geoms.append(geom2)
                geom3 = self.buffer(geom2)
                geom3.translate(dx=deplace, dy=-deplace)
                geom4 = geom3.intersection(unionGeom)
                # Append to get the union of intersected geometries
                # Necessary 2 operations because geom4 will be changed in the future
                geom4_for_temp = geom3.intersection(unionGeom)
                temp.append(geom4_for_temp)
                # Return to old projection and add on provider
                geom4.transform(tr_volta)
                feat_translated = QgsFeature()
                feat_translated.setGeometry(geom4)
                provider.addFeature(feat_translated)
        unionTranslatedGeom = QgsGeometry.unaryUnion(temp)
        # Fill the area created by the translation

        additional = self.fillGeometries(temp_geoms, unionGeom, unionTranslatedGeom, deplace)
        for add_geom in additional:
            add_geom.transform(tr_volta)
            feat = QgsFeature()
            feat.setGeometry(add_geom)
            provider.addFeature(feat)
        temp_layer.commitChanges()
        QgsProject.instance().addMapLayer(temp_layer)
        



layer = iface.activeLayer()
generate = GenerateDivisions(
    layer, 
    4, #divisoes
    500, #sobreposicao
    0.3, #deslocamento
    True #apenas_selecionado
)
if generate.parameterValidation():
    generate.runProcess()