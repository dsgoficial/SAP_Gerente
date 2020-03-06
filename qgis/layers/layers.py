from qgis import gui, core
from qgis.utils import plugins, iface
from Ferramentas_Gerencia.qgis.interfaces.ILayers import ILayers

class Layers(ILayers):
    
    def __init__(self):
        super(Layers, self).__init__()

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

    def addLayerGroup(self, groupName, parentGroup=None):
        if parentGroup is None:
            tree = core.QgsProject.instance().layerTreeRoot()
            return tree.addGroup(groupName)
        return parentGroup.addGroup(groupName)

    def getUri(self, dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable):
        return u"""dbname='{}' host={} port={} user='{}' password='{}' key='id' table="{}"."{}" (geom) sql= """.format(
            dbName, 
            dbHost, 
            dbPort, 
            dbUser,
            dbPassword,
            dbSchema,
            dbTable
        )

    def loadLayer(self, dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable, groupParent=None):
        lyr = core.QgsVectorLayer(
            self.getUri(dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable), 
            dbTable, 
            u"postgres"
        )
        if groupParent is None:
            return core.QgsProject.instance().addMapLayer(lyr)
        layer = core.QgsProject.instance().addMapLayer(lyr, False)
        groupParent.addLayer(layer)
        return layer