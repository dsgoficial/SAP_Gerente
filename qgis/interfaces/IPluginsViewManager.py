from abc import ABC, abstractmethod

class IPluginsViewManager(ABC):
    
    @abstractmethod
    def addDockWidget(self, dockWidget):
        pass
    
    @abstractmethod
    def removeDockWidget(self, dockWidget):
        pass