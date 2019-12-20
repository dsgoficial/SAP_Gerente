from Ferramentas_Gerencia.sap.views.dock.interfaces.IManagementDock import IManagementDock

import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class ManagementDock(QtWidgets.QDockWidget, IManagementDock):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'uis',
        'managementDock.ui'
    )

    tab_icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'icons',
        'DSG.svg'
    )

    item_icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'icons',
        'config.png'
    )

    def __init__(self):
        super(ManagementDock, self).__init__()
        uic.loadUi(self.dialog_path, self)
        self.tabWidget.setTabIcon(0, QtGui.QIcon(self.tab_icon_path))
        self.tabWidget.setTabIcon(1, QtGui.QIcon(self.tab_icon_path))
        self.tabWidget.setTabIcon(2, QtGui.QIcon(self.tab_icon_path))
        self.tabWidget.setTabIcon(3, QtGui.QIcon(self.tab_icon_path))

        self.treeWidgetManagement = QtWidgets.QTreeWidget()
        self.treeWidgetManagement.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.treeWidgetManagement.setColumnCount(1)
        self.treeWidgetManagement.header().hide()
        self.projectTab.layout().addWidget(self.treeWidgetManagement)

        self.treeWidgetCreation = QtWidgets.QTreeWidget()
        self.treeWidgetCreation.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.treeWidgetCreation.setColumnCount(1)
        self.treeWidgetCreation.header().hide()
        self.creationTab.layout().addWidget(self.treeWidgetCreation)

        self.treeWidgetDanger = QtWidgets.QTreeWidget()
        self.treeWidgetDanger.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.treeWidgetDanger.setColumnCount(1)
        self.treeWidgetDanger.header().hide()
        self.dangerZoneTab.layout().addWidget(self.treeWidgetDanger)

    def addProjectManagementWidget(self, name, widget):
        topLevelItem = QtWidgets.QTreeWidgetItem([name])
        topLevelItem.setIcon(0, QtGui.QIcon(self.item_icon_path))
        childItem = QtWidgets.QTreeWidgetItem()
        topLevelItem.addChild(childItem)
        self.treeWidgetManagement.addTopLevelItem(topLevelItem)
        self.treeWidgetManagement.setItemWidget(childItem, 0, widget)

    def addProjectCreationWidget(self, name, widget):
        topLevelItem = QtWidgets.QTreeWidgetItem([name])
        topLevelItem.setIcon(0, QtGui.QIcon(self.item_icon_path))
        childItem = QtWidgets.QTreeWidgetItem()
        topLevelItem.addChild(childItem)
        self.treeWidgetCreation.addTopLevelItem(topLevelItem)
        self.treeWidgetCreation.setItemWidget(childItem, 0, widget)

    def addDangerZoneWidget(self, name, widget):
        topLevelItem = QtWidgets.QTreeWidgetItem([name])
        topLevelItem.setIcon(0, QtGui.QIcon(self.item_icon_path))
        childItem = QtWidgets.QTreeWidgetItem()
        topLevelItem.addChild(childItem)
        self.treeWidgetDanger.addTopLevelItem(topLevelItem)
        self.treeWidgetDanger.setItemWidget(childItem, 0, widget)

    def showMessageErro(self, title, text):
        QtWidgets.QMessageBox.critical(
            self,
            title, 
            text
        )

    def showMessageInfo(self, title, text):
        QtWidgets.QMessageBox.information(
            self,
            title, 
            text
        )