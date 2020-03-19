from abc import ABC, abstractmethod

class IMapTool(ABC):

    @abstractmethod
    def start(self, *args):
       pass