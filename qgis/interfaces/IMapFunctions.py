from abc import ABC, abstractmethod

class IMapFunctions(ABC):

    @abstractmethod
    def run(self, *args):
       pass