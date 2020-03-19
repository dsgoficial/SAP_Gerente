
from abc import ABC, abstractmethod

class IStyles(ABC):

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