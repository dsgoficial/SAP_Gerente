from abc import ABC, abstractmethod

class GisCtrlInterface(ABC):

    """ @abstractmethod
    def setVariable(self, key, value):
        pass

    @abstractmethod
    def getVariable(self, key):
        pass """

    @abstractmethod
    def getVersion(self, key):
        pass

    @abstractmethod
    def getPluginsVersions(self, key):
        pass