from PyQt5 import QtCore

from Ferramentas_Gerencia.widgets.mDock import MDock

class MDockBuilder:

    def __init__(self):
        super(MDockBuilder, self).__init__()
        self.dockSap = MDock()

    def getInstance(self):
        return self.dockSap

    def setController(self, controller):
        self.dockSap.setController(controller)

    def addProjectManagementWidget(self, name, widget):
        self.dockSap.addProjectManagementWidget(name, widget)

    def addProjectCreationWidget(self, name, widget):
        self.dockSap.addProjectCreationWidget(name, widget)

    def addDangerZoneWidget(self, name, widget):
        self.dockSap.addDangerZoneWidget(name, widget)

    def getResult(self):
        return self.dockSap