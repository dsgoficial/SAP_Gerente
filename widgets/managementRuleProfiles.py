# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.managementDialog  import ManagementDialog

class ManagementRuleProfiles(ManagementDialog):
    
    def __init__(self, sapCtrl):
        super(ManagementRuleProfiles, self).__init__(controller=sapCtrl)
        self.subphases = []
        self.groupData = []

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'managementRuleProfiles.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def getSubphases(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.subphases
        ]

    def setGroupData(self, groupData):
        self.groupData = groupData

    def getGroupData(self):
        return [
            {
                'name': d['grupo_regra'],
                'value': d['id'],
                'data': d
            }
            for d in self.groupData
        ]

    def createCombobox(self, row, col, mapValues, currentValue, handle=None ):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        combo = QtWidgets.QComboBox(self.tableWidget)
        combo.setFixedSize(QtCore.QSize(200, 30))
        if mapValues:
            for data in mapValues:
                combo.addItem(data['name'], data['value'])
            combo.setCurrentIndex(combo.findData(currentValue))
        if handle:
            index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, col))
            combo.currentIndexChanged.connect(
                lambda *args, combo=combo, index=index: handle(combo, index)
            )
        layout.addWidget(combo)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def addRow(self, profileId, ruleGroupId, subphaseId):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(profileId))
        self.tableWidget.setCellWidget(idx, 1, self.createCombobox(idx, 1, self.getGroupData(), ruleGroupId) )
        self.tableWidget.setCellWidget(idx, 2, self.createCombobox(idx, 2, self.getSubphases(), subphaseId) )

    def addRows(self, profiles):
        self.clearAllItems()
        for modelProfile in profiles:
            self.addRow(
                modelProfile['id'],
                modelProfile['grupo_regra_id'],
                modelProfile['subfase_id']
            )
        self.adjustColumns()

    def getRowIndex(self, profileId):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    profileId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'id': self.tableWidget.model().index(rowIndex, 0).data(),
            'grupo_regra_id': self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().currentIndex()
            ),
            'subfase_id': self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().currentIndex()
            )
        }
    
    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'grupo_regra_id': int(row['grupo_regra_id']),
                'subfase_id': int(row['subfase_id']),
            }
            for row in self.getAllTableData()
            if row['id']
        ]

    def removeSelected(self):
        rowsIds = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rowsIds.append(int(self.getRowData(qModelIndex.row())['id']))
            self.tableWidget.removeRow(qModelIndex.row())
        if not rowsIds:
            return
        self.controller.deleteSapRuleProfiles(rowsIds)

    def openAddForm(self):
        self.controller.addRuleProfile()
    
    def saveTable(self):
        updatedProfiles = self.getUpdatedRows()
        print(updatedProfiles)
        if updatedProfiles:
            self.controller.updateSapRuleProfiles(
                updatedProfiles
            )
        