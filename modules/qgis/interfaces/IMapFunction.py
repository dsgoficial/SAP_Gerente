from abc import ABC, abstractmethod

class IMapFunction(ABC):

    @abstractmethod
    def run(self, *args):
       pass