# -*- coding: utf-8 -*-

import os, sys
from qgis import core, gui
from PyQt5 import QtCore
from Ferramentas_Gerencia.SAP.management import Management

class Main(QtCore.QObject):
    def __init__(self, iface):
        super(Main, self).__init__()
        self.plugin_dir = os.path.dirname(__file__)
        self.iface = iface
        self.sap = Management(self.iface)

    def initGui(self):
        self.sap.add_action_qgis(True)
        
    def unload(self):
        self.sap.add_action_qgis(False)