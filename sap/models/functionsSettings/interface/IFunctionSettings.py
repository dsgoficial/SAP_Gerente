from abc import ABC, abstractmethod

class IFunctionSettings(ABC):

    @abstractmethod
    def getLayersOptions(self):
       pass