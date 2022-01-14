from PyQt5 import QtCore

from Ferramentas_Gerencia.interfaces.IManagementDockBuilder import IManagementDockBuilder

from Ferramentas_Gerencia.widgets.managementDock import ManagementDock

class ManagementDockBuilder(IManagementDockBuilder):

    def __init__(self):
        super(ManagementDockBuilder, self).__init__()
        self.dockSapManagement = ManagementDock()

    def getInstance(self):
        return self.dockSapManagement

    def setController(self, controller):
        self.dockSapManagement.setController(controller)

    def addProjectManagementWidget(self, name, widget):
        self.dockSapManagement.addProjectManagementWidget(name, widget)

    def addProjectCreationWidget(self, name, widget):
        self.dockSapManagement.addProjectCreationWidget(name, widget)

    def addDangerZoneWidget(self, name, widget):
        self.dockSapManagement.addDangerZoneWidget(name, widget)

    def getResult(self):
        return self.dockSapManagement