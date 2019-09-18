# -*- coding: utf-8 -*-
from PyQt5 import QtCore, uic, QtWidgets, QtGui
import sys, os, pickle
from Ferramentas_Gerencia.SAP.Views.sapDocker import SapDocker
from Ferramentas_Gerencia.SAP.Views.sapAction import SapAction

from Ferramentas_Gerencia.SAP.Login.login import Login
from Ferramentas_Gerencia.SAP.Project.management import Management

class Sap(QtCore.QObject):

    def __init__(self, iface):
        super(Sap, self).__init__()
        self.iface = iface
        self.sapDocker = SapDocker(self.iface)
        self.management = Management(self.iface)
        self.login = Login(self.iface)
        self.login.open_sap_management.connect(
            self.add_docker_on_qgis
        )
        self.sapAction = SapAction(self.iface)
        self.sapAction.show_sap_management.connect(
            self.login_sap
        )
    
    def login_sap(self):
        self.login.show_login_dialog()

    def add_docker_on_qgis(self):
        self.sapDocker.tab.layout().addWidget(self.management.get_tree_widget())
        self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.sapDocker)

    def add_action_on_qgis(self):
        self.iface.digitizeToolBar().addAction(
            self.sapAction
        )
    
    def remvoe_action_on_qgis(self):
        self.iface.digitizeToolBar().removeAction(
            self.sapAction
        )
   
    