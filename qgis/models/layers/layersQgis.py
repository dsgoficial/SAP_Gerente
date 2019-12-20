from qgis import gui, core
from qgis.utils import plugins, iface

class LayersQgis:
    
    def isActiveLayer(self, layerName):
        activeLayer = iface.activeLayer()
        return activeLayer and layerName in activeLayer.dataProvider().uri().table()

    def getActiveLayerSelections(self):
        if not iface.activeLayer():
            return []
        return iface.activeLayer().selectedFeatures()

    def getFieldValuesFromSelections(self, fieldName):
        values = []
        for feature in self.getActiveLayerSelections():
            values.append(feature[fieldName])
        return values

    def getFieldsNamesFromSelection(self, filterText=""):
        if not len(self.getActiveLayerSelections()) > 0:
            return []
        feature = self.getActiveLayerSelections()[0]
        if filterText:
            return [ name for name in feature.fields().names() if filterText in name ]
        return [ name for name in feature.fields().names() ]

    def getLayersTreeSelection(self):
        return iface.layerTreeView().selectedLayers()
    
    def isValidLayer(self, layer, layerSchema, layerName):
        return layer.dataProvider().uri().table() == layerName and layer.dataProvider().uri().schema() == layerSchema

    def findVectorLayer(self, layerSchema, layerName):
        layers = []
        for layer in core.QgsProject.instance().mapLayers().values():
            if self.isValidLayer(layer, layerSchema, layerName):
                layers.append(layer) 
        return layers