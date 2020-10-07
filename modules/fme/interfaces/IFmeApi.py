from abc import ABC, abstractmethod

class IFmeApi(ABC):
    
    @abstractmethod
    def httpGet(self, url): 
        pass

    @abstractmethod
    def setServer(self, server, port=''):
        pass

    @abstractmethod
    def getServer(self):
        pass

    @abstractmethod
    def getRoutines(self):
        pass