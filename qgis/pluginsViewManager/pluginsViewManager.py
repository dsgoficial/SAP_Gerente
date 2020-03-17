from PyQt5 import QtCore
from qgis.utils import plugins, iface

from Ferramentas_Gerencia.qgis.interfaces.IPluginsViewManager import IPluginsViewManager

class PluginsViewManager(IPluginsViewManager):

    def __init__(self):
        super(PluginsViewManager, self).__init__()

    def addDockWidget(self, dockWidget):
        iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget)
    
    def removeDockWidget(self, dockWidget):
        if not dockWidget.isVisible():
            return
        iface.removeDockWidget(dockWidget)