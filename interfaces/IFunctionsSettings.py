from abc import ABC, abstractmethod

class IFunctionsSettings(ABC):

    @abstractmethod
    def getSettings(self):
       pass