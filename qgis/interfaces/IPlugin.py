from abc import ABC, abstractmethod

class IPlugin(ABC):
    
    @abstractmethod
    def run(self, *args):
        pass