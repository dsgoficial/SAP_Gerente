from abc import ABC, abstractmethod

class IQgisApi(ABC):
    
    @abstractmethod
    def getVersion(self):
        pass

    @abstractmethod
    def getPluginsVersions(self):
        pass

    @abstractmethod
    def setProjectVariable(self, key, value):
       pass

    @abstractmethod
    def getProjectVariable(self, key):
        pass

    @abstractmethod
    def setSettingsVariable(self, key, value):
        pass

    @abstractmethod
    def getSettingsVariable(self, key):
        pass

    @abstractmethod
    def getQmlStyleFromLayers(self, layers):
        pass

    @abstractmethod
    def getQmlStyleFromLayer(self, layer):
        pass

    @abstractmethod
    def setQmlStyleToLayer(self, layer, qml):
        pass

    @abstractmethod
    def getSldStyleFromLayer(self, layer):
        pass

    @abstractmethod
    def setSldStyleToLayer(self, layer, sld):
        pass

    @abstractmethod
    def isActiveLayer(self, layerName):
        pass

    @abstractmethod
    def getActiveLayerAttribute(self, featureId, fieldName):
        pass

    @abstractmethod
    def getActiveLayerSelections(self):
        pass
    
    @abstractmethod
    def getCrsId(self):
        pass

    @abstractmethod
    def getActiveLayerAllFeatures(self):
        pass

    @abstractmethod
    def isPolygon(self):
        pass

    @abstractmethod
    def getFieldValuesFromSelections(self, fieldName):
        pass

    @abstractmethod
    def getFieldsNamesFromSelection(self, filterText=""):
        pass

    @abstractmethod
    def getLayersTreeSelection(self):
        pass
    
    @abstractmethod
    def isValidLayer(self, layer, layerSchema, layerName):
        pass

    @abstractmethod
    def findVectorLayer(self, layerSchema, layerName):
        pass

    @abstractmethod
    def addLayerGroup(self, groupName, parentGroup=None):
        pass

    @abstractmethod
    def getUri(self, dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable):
        pass

    @abstractmethod
    def loadPostgresLayer(self, dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable, groupParent=None):
        pass

    @abstractmethod
    def addLayerOnMap(self, layer):
        pass

    @abstractmethod
    def addFeature(self, layer, fieldValues, geometry):
        pass