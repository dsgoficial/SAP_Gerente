# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.sap.dialogs.managementDialog  import ManagementDialog

class ManagementRuleSet(ManagementDialog):
    
    def __init__(self, sapCtrl, parent=None):
        super(ManagementRuleSet, self).__init__(sapCtrl=sapCtrl, parent=parent)
        self.parent = parent
        self.tableWidget.setColumnHidden(1, True)
        #self.tableWidget.setColumnHidden(3, True)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'managementRulesGroup.ui'
        )

    def createColorBtn(self, row, col, colorRgb):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        button = QtWidgets.QPushButton('', self.tableWidget)
        button.setStyleSheet("QPushButton {background-color: rgb("+colorRgb+")}")
        index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, col))
        button.clicked.connect(
            lambda *args, index=index: self.handleColorBtn(index)
        )
        layout.addWidget(button)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def handleColorBtn(self, index):
        colorItem = self.tableWidget.model().index(index.row(), 1)
        oldColorRgb = colorItem.data()
        r, g, b = oldColorRgb.split(',')
        colorDlg = QtWidgets.QColorDialog()
        colorDlg.setCurrentColor(QtGui.QColor(int(r), int(g), int(b)))
        if not colorDlg.exec():
            return
        r, g, b, _ = colorDlg.selectedColor().getRgb()
        newColorRgb = "{0},{1},{2}".format(r, g, b)
        self.tableWidget.setItem(index.row(), 1, self.createNotEditableItem(newColorRgb))
        self.tableWidget.setCellWidget(index.row(), 2, self.createColorBtn(index.row(), 2, newColorRgb))

    def getColumnsIndexToSearch(self):
        return list(range(1))

    def addRow(self, ruleGroup, colorRgb, count):
        idx = self.tableWidget.rowCount()
        self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createEditableItem(ruleGroup))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(colorRgb))
        self.tableWidget.setCellWidget(idx, 2, self.createColorBtn(idx, 2, colorRgb))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(count))

    def addRows(self, groupData):
        self.clearAllItems()
        for group in groupData:  
            self.addRow(group['grupo_regra'], group['cor_rgb'], str(group['count']))
        self.adjustColumns()

    def getRowData(self, rowIndex):
        return {
            'grupo_regra': self.tableWidget.model().index(rowIndex, 0).data(),
            'cor_rgb': self.tableWidget.model().index(rowIndex, 1).data()
        }

    def removeSelected(self):
        deleteErro = False
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            count = int(self.tableWidget.model().index(qModelIndex.row(), 3).data())
            if count > 0:
                deleteErro = True
                self.tableWidget.item(qModelIndex.row(), qModelIndex.column()).setSelected(False)
                continue
            self.tableWidget.removeRow(qModelIndex.row())
        if deleteErro:
            self.showError('Erro', 'Delete todas as regras do grupo que será removido!')

    def getGroupList(self):
        return [
            d['grupo_regra']
            for d in self.getAllTableData()
        ]

    def openAddForm(self):
        self.sapCtrl.addRuleSet(
            self.getGroupList()
        )

    def saveTable(self):
        self.parent.setGroupData(self.getAllTableData())
        self.accept()
