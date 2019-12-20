from PyQt5 import QtCore
from qgis.utils import plugins, iface

from Ferramentas_Gerencia.qgis.views.plugins.interface.pluginViewInterface import PluginViewInterface

class PluginViewQgis(PluginViewInterface):


    def addDockWidget(self, dockWidget):
        iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget)
    
    def removeDockWidget(self, dockWidget):
        if not dockWidget.isVisible():
            return
        iface.removeDockWidget(dockWidget)

    