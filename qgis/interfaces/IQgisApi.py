from abc import ABC, abstractmethod

class IQgisApi(ABC):
    
    @abstractmethod
    def setLayers(self, layers):
        pass

    @abstractmethod
    def getLayers(self):
        pass
    
    @abstractmethod
    def setStyles(self, styles):
        pass

    @abstractmethod
    def getStyles(self):
        pass
    
    @abstractmethod
    def setStorages(self, storages):
        pass

    @abstractmethod
    def getStorages(self):
        pass

    @abstractmethod
    def getVersion(self):
        pass

    @abstractmethod
    def getPluginsVersions(self):
        pass