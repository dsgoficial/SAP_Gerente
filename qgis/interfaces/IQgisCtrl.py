from abc import ABC, abstractmethod

class IQgisCtrl(ABC):

    @abstractmethod
    def loadApiQgis(self):
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
    def getVersion(self):
        pass
    
    @abstractmethod
    def getPluginsVersions(self):
        pass

    @abstractmethod
    def addDockWidget(self, dockWidget):
        pass

    @abstractmethod
    def removeDockWidget(self, dockWidget):
        pass

    @abstractmethod
    def getFieldValuesFromLayer(self, layerName, fieldName, allSelection, chooseAttribute):
        pass

    @abstractmethod
    def getQmlStyleFromLayersTreeSelection(self):
        pass

    @abstractmethod
    def applyStylesOnLayers(self, stylesData):
        pass

    @abstractmethod
    def getWidgetByName(self):
        pass

    @abstractmethod
    def activeMapToolByToolName(self, toolName):
        pass

    @abstractmethod
    def addLayerGroup(self, groupName, parentGroup=None):
        pass
    
    @abstractmethod
    def loadLayer(self, dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable, groupParent=None):
        pass

    @abstractmethod
    def startSapFP(self, activityData):
        pass

    @abstractmethod
    def getActiveLayerAttribute(self, featureId, fieldName):
        pass

    @abstractmethod
    def generateWorkUnit(self, layerName, size, overlay, deplace, prefixName, onlySelected):
        pass