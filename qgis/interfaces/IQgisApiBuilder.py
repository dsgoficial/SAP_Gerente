from abc import ABC, abstractmethod

class IQgisApiBuilder(ABC):
    
    @abstractmethod
    def setStyles(self, styles):
        pass

    @abstractmethod
    def setLayers(self, layers):
        pass
    
    @abstractmethod
    def setStorages(self, storages):
        pass

    @abstractmethod
    def getResult(self):
        pass