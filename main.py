# -*- coding: utf-8 -*-

import os, sys
from qgis import core, gui
from PyQt5 import QtCore
from Ferramentas_Gerencia.SAP.sap import Sap

class Main(QtCore.QObject):
    def __init__(self, iface):
        super(Main, self).__init__()
        self.plugin_dir = os.path.dirname(__file__)
        self.iface = iface
        self.sap = Sap(self.iface)

    def initGui(self):
        self.sap.add_action_on_qgis()
        
    def unload(self):
        self.sap.remove_action_on_qgis()