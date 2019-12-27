# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.sap.views.dialogs.managementDialog  import ManagementDialog

class ManagementRulesGroup(ManagementDialog):
    
    def __init__(self, sapCtrl):
        super(ManagementRulesGroup, self).__init__(sapCtrl=sapCtrl)
        self.tableWidget.setColumnHidden(5, True)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis',
            'managementRulesGroup.ui'
        )

    def getColorIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'icons',
            'colorPicker.png'
        )

    def createColorBtn(self, row, col):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        button = QtWidgets.QPushButton('', self.tableWidget)
        button.setIcon(QtGui.QIcon(self.getUploadIconPath()))
        button.setFixedSize(QtCore.QSize(30, 30))
        button.setIconSize(QtCore.QSize(20, 20))
        index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, col))
        button.clicked.connect(
            lambda *args, index=index: self.handleColorBtn(index)
        )
        layout.addWidget(button)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def handleColorBtn(self, index):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            print(color.name())

    def getColumnsIndexToSearch(self):
        return list(range(1))

    def addRow(self, ruleGroup, colorRgb):
        idx = self.getRowIndex('')
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createEditableItem(ruleGroup))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(colorRgb))
        self.tableWidget.setCellWidget(idx, 2, self.createColorBtn(idx, 2))
        

    def getRowIndex(self, ruleId):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    ruleId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'grupo_regra': self.tableWidget.model().index(rowIndex, 0).data(),
            'cor': self.tableWidget.model().index(rowIndex, 1).data()
        }

    def openAddForm(self):
        pass

    def saveTable(self):
        pass