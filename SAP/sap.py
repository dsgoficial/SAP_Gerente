# -*- coding: utf-8 -*-
from PyQt5 import QtCore, uic, QtWidgets, QtGui
import sys, os, pickle
from qgis import core, gui
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
        self.sapAction = SapAction(self.iface)
        self.connect_signals()

    def connect_signals(self):
        self.login.open_sap_management.connect(
            self.add_docker_on_qgis
        )
        self.sapAction.show_sap_management.connect(
            self.login_sap
        )
        self.iface.actionNewProject().triggered.connect(
            self.remove_docker_on_qgis
        )
        core.QgsProject.instance().readProject.connect(
            self.remove_docker_on_qgis
        )
    
    def login_sap(self):
        self.login.show_login_dialog()

    def add_docker_on_qgis(self):
        if self.sapDocker.isVisible():
            return
        self.curr_man_tree = self.management.get_tree_widget()
        self.sapDocker.tab.layout().addWidget(self.curr_man_tree)
        self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.sapDocker)

    def remove_docker_on_qgis(self):
        if not self.sapDocker.isVisible():
            return
        self.iface.removeDockWidget(self.sapDocker)
        self.sapDocker.tab.layout().removeWidget(self.curr_man_tree)

    def add_action_on_qgis(self):
        self.iface.digitizeToolBar().addAction(
            self.sapAction
        )
    
    def remvoe_action_on_qgis(self):
        self.iface.digitizeToolBar().removeAction(
            self.sapAction
        )
   
    