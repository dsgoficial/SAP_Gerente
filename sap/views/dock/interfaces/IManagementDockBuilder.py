from abc import ABC, abstractmethod


class IManagementDockBuilder(ABC):

    @abstractmethod
    def getResult(self):
        pass

    @abstractmethod
    def addProjectManagementWidget(self, name, widget):
        pass

    @abstractmethod
    def addProjectCreationWidget(self, name, widget):
        pass

    @abstractmethod
    def addDangerZoneWidget(self, name, widget):
        pass