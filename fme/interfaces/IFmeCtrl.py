from abc import ABC, abstractmethod

class IFmeCtrl(ABC):
    
    @abstractmethod
    def getRoutines(self, server, port):
        pass