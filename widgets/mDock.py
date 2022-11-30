from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory

import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class MDock(QtWidgets.QDockWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        'uis',
        'mDock.ui'
    )

    tab_icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'icons',
        'DSG.svg'
    )

    item_icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'icons',
        'config.png'
    )

    def __init__(self,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(MDock, self).__init__()
        uic.loadUi(self.dialog_path, self)
        self.messageFactory = messageFactory
        self.tabWidget.setTabIcon(0, QtGui.QIcon(self.tab_icon_path))
        self.tabWidget.setTabIcon(1, QtGui.QIcon(self.tab_icon_path))
        self.tabWidget.setTabIcon(2, QtGui.QIcon(self.tab_icon_path))
        #self.tabWidget.setTabIcon(3, QtGui.QIcon(self.tab_icon_path))
        self.tabWidget.removeTab(3)
        
        self.treeWidgetManagement = QtWidgets.QTreeWidget()
        self.treeWidgetManagement.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.treeWidgetManagement.setColumnCount(1)
        self.treeWidgetManagement.header().hide()
        self.treeWidgetManagement.itemDoubleClicked.connect(self.onItemClicked)

        self.connectQtreeWidgetSignals(self.treeWidgetManagement)
        self.projectTab.layout().addWidget(self.treeWidgetManagement)

        self.treeWidgetCreation = QtWidgets.QTreeWidget()
        self.treeWidgetCreation.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.treeWidgetCreation.setColumnCount(1)
        self.treeWidgetCreation.header().hide()
        self.treeWidgetCreation.itemDoubleClicked.connect(self.onItemClicked)
        self.connectQtreeWidgetSignals(self.treeWidgetCreation)
        self.creationTab.layout().addWidget(self.treeWidgetCreation)

        self.treeWidgetDanger = QtWidgets.QTreeWidget()
        self.treeWidgetDanger.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.treeWidgetDanger.setColumnCount(1)
        self.treeWidgetDanger.header().hide()
        self.treeWidgetDanger.itemDoubleClicked.connect(self.onItemClicked)
        self.connectQtreeWidgetSignals(self.treeWidgetDanger)
        self.dangerZoneTab.layout().addWidget(self.treeWidgetDanger)
        self.widgets = {}
        self.active = None

    def onItemClicked(self, it, col):
        self.active.close() if self.active else None
        self.active = self.widgets[it.text(col)]()
        self.active.show()

    def setController(self, controller):
        self.controller = controller

    def getController(self):
        return self.controller

    def closeEvent(self, e):
        self.getController().disableMenuBar(True)
        self.closeChildren(QtWidgets.QDialog)
        super().closeEvent(e)
        
    def closeChildren(self, typeWidget):
        [ d.close() for d in self.findChildren(typeWidget) ]

    def connectQtreeWidgetSignals(self, treeWidget):
        treeWidget.itemExpanded.connect(
            self.handleItemExpanded
        )

    def disconnectQtreeWidgetSignals(self, treeWidget):
        treeWidget.itemExpanded.disconnect(
            self.handleItemExpanded
        )

    def handleItemExpanded(self, item):
        treeWidget = self.sender()
        treeWidget.collapseAll()
        self.disconnectQtreeWidgetSignals(treeWidget)
        item.setExpanded(True)
        self.connectQtreeWidgetSignals(treeWidget)

    def addProjectManagementWidget(self, name, widget):
        self.widgets[name] = widget
        topLevelItem = QtWidgets.QTreeWidgetItem([name])
        topLevelItem.setIcon(0, QtGui.QIcon(self.item_icon_path))
        # childItem = QtWidgets.QTreeWidgetItem()
        # topLevelItem.addChild(childItem)
        self.treeWidgetManagement.addTopLevelItem(topLevelItem)
        #self.treeWidgetManagement.setItemWidget(childItem, 0, widget)

    def addProjectCreationWidget(self, name, widget):
        self.widgets[name] = widget
        topLevelItem = QtWidgets.QTreeWidgetItem([name])
        topLevelItem.setIcon(0, QtGui.QIcon(self.item_icon_path))
        # childItem = QtWidgets.QTreeWidgetItem()
        # topLevelItem.addChild(childItem)
        self.treeWidgetCreation.addTopLevelItem(topLevelItem)
        #self.treeWidgetCreation.setItemWidget(childItem, 0, widget)

    def addDangerZoneWidget(self, name, widget):
        self.widgets[name] = widget
        topLevelItem = QtWidgets.QTreeWidgetItem([name])
        topLevelItem.setIcon(0, QtGui.QIcon(self.item_icon_path))
        # childItem = QtWidgets.QTreeWidgetItem()
        # topLevelItem.addChild(childItem)
        self.treeWidgetDanger.addTopLevelItem(topLevelItem)
        #self.treeWidgetDanger.setItemWidget(childItem, 0, widget)

    def showError(self, title, text):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, text)

    def showInfo(self, title, text):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, text)

    @QtCore.pyqtSlot(str)
    def on_searchProjectManagementLe_textEdited(self, text):
        self.searchItems(text, self.treeWidgetManagement)

    @QtCore.pyqtSlot(str)
    def on_searchProjectCreationLe_textEdited(self, text):
        self.searchItems(text, self.treeWidgetCreation)

    @QtCore.pyqtSlot(str)
    def on_searchDangerZoneLe_textEdited(self, text):
        self.searchItems(text, self.treeWidgetDanger)
        
    def searchItems(self, text, tree):
        for idx in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(idx)
            if text and not( text.lower() in item.text(0).lower()):
                item.setHidden(True)
            else:
                item.setHidden(False)

