from abc import ABC, abstractmethod

class StoragesInterface(ABC):

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