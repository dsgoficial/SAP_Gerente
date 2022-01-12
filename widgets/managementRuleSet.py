# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.managementDialog  import ManagementDialog

class ManagementRuleSet(ManagementDialog):
    
    def __init__(self, sapCtrl, parent=None):
        super(ManagementRuleSet, self).__init__(controller=sapCtrl, parent=parent)
        self.parent = parent
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(2, True)

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
        colorItem = self.tableWidget.model().index(index.row(), 2)
        oldColorRgb = colorItem.data()
        r, g, b = oldColorRgb.split(',')
        colorDlg = QtWidgets.QColorDialog()
        colorDlg.setCurrentColor(QtGui.QColor(int(r), int(g), int(b)))
        if not colorDlg.exec():
            return
        r, g, b, _ = colorDlg.selectedColor().getRgb()
        newColorRgb = "{0},{1},{2}".format(r, g, b)
        self.tableWidget.setItem(index.row(), 2, self.createNotEditableItem(newColorRgb))
        self.tableWidget.setCellWidget(index.row(), 3, self.createColorBtn(index.row(), 2, newColorRgb))

    def getColumnsIndexToSearch(self):
        return list(range(1))

    def addRow(self, ruleSetId, ruleGroup, colorRgb, count, order):
        idx = self.tableWidget.rowCount()
        self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(ruleSetId))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(ruleGroup))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(colorRgb))
        self.tableWidget.setCellWidget(idx, 3, self.createColorBtn(idx, 2, colorRgb))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(count))
        self.tableWidget.setItem(idx, 5, self.createEditableItem(order))

    def addRows(self, groupData):
        self.clearAllItems()
        for group in groupData:  
            self.addRow(
                group['id'], 
                group['grupo_regra'], 
                group['cor_rgb'], 
                str(self.parent.countRulesByGroup(group['grupo_regra'])),
                group['ordem'] 
            )
        self.adjustColumns()

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'grupo_regra': self.tableWidget.model().index(rowIndex, 1).data(),
            'cor_rgb': self.tableWidget.model().index(rowIndex, 2).data(),
            'ordem': int(self.tableWidget.model().index(rowIndex, 5).data())
        }

    def removeSelected(self):
        deletedIds = []
        deleteErro = False
        while self.tableWidget.selectionModel().selectedRows() :
            qModelIndex = self.tableWidget.selectionModel().selectedRows()[0]
            count = int(self.tableWidget.model().index(qModelIndex.row(), 4).data())
            if count > 0:
                deleteErro = True
                self.tableWidget.selectionModel().select(
                    qModelIndex, 
                    QtCore.QItemSelectionModel.Deselect
                )
                continue
            deletedIds.append(int(self.tableWidget.model().index(qModelIndex.row(), 0).data()))
            self.tableWidget.removeRow(qModelIndex.row())
        self.controller.deleteSapRuleSet(deletedIds) if deletedIds else ''
        self.showError('Erro', 'Delete todas as regras do grupo que será removido!') if deleteErro else ''

    def openAddForm(self):
        self.controller.addRuleSet()

    def saveTable(self):
        self.controller.updateSapRuleSet( self.getAllTableData() )
