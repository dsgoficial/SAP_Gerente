import os, sys
from qgis import core, gui
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

from SAP_Gerente.modules.qgis.qgisCtrl import QgisCtrl
from SAP_Gerente.modules.sap.api.sapHttp import SapHttp
from SAP_Gerente.modules.fme.fmeCtrl import FmeCtrl
from SAP_Gerente.config import Config
from SAP_Gerente.controllers.mToolCtrl import MToolCtrl

class Main(QObject):

    def __init__(self, iface):
        super(Main, self).__init__()
        self.plugin_dir = os.path.dirname(__file__)
        self.iface = iface
        
        """ self.action = QAction(
            QIcon(self.path_icon),
            "SAP Gerente",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(
            self.startPlugin
        ) """

        self.qgisCtrl = QgisCtrl()
        self.fmeCtrl = FmeCtrl()
        self.sapCtrl = SapHttp(
            qgis = self.qgisCtrl,
            fmeCtrl = self.fmeCtrl
        )

        self.managementToolCtrl = MToolCtrl(
            qgis=self.qgisCtrl,
            fmeCtrl=self.fmeCtrl,
            sapCtrl=self.sapCtrl
        )

    def initGui(self):
        self.qgisCtrl.load()
        self.action = self.qgisCtrl.createAction(
            Config.NAME,
            self.getPluginIconPath(),
            self.startPlugin
            
        )
        self.qgisCtrl.addActionToolBar(self.action)
        
    def unload(self):
        self.qgisCtrl.removeActionToolBar(
            self.action
        )
        self.qgisCtrl.removeToolBar()
        self.managementToolCtrl.removeDockSap()

    def startPlugin(self): 
        if not self.sapCtrl.login():
            return
        self.managementToolCtrl.loadDockSap()

    def getPluginIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.join(
                os.path.dirname(__file__)
            )),
            'icons',
            'icon.png'
        )