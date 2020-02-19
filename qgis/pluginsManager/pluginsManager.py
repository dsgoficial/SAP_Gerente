from PyQt5 import QtCore
from qgis.utils import plugins, iface

from Ferramentas_Gerencia.qgis.interfaces.IPluginsManager import IPluginsManager

class PluginsManager(IPluginsManager):

    def __init__(self):
        super(PluginsManager, self).__init__()

    def addDockWidget(self, dockWidget):
        iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget)
    
    def removeDockWidget(self, dockWidget):
        if not dockWidget.isVisible():
            return
        iface.removeDockWidget(dockWidget)

    