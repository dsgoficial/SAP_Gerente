# -*- coding: utf-8 -*-
import os, sys
from qgis import core, gui
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

from Ferramentas_Gerencia.qgis.controllers.qgisCtrl import QgisCtrl
from Ferramentas_Gerencia.sap.controllers.sapManagerCtrl import SapManagerCtrl

class Main(QObject):

    path_icon = os.path.join(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__)
        )),
        'icon.png'
    )

    def __init__(self, iface):
        super(Main, self).__init__()
        self.plugin_dir = os.path.dirname(__file__)
        self.iface = iface
        self.action = QAction(
            QIcon(self.path_icon),
            "Ferramentas de Gerência",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(
            self.startPlugin
        )

    def initGui(self):
        self.iface.digitizeToolBar().addAction(
            self.action
        )
        
    def unload(self):
        self.iface.digitizeToolBar().removeAction(
            self.action
        )

    def startPlugin(self):
        self.qgisCtrl = QgisCtrl()
        self.sapManagerCtrl = SapManagerCtrl(
            gisPlatform=self.qgisCtrl
        )
        self.sapManagerCtrl.showLoginView()