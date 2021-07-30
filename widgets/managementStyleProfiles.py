# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.managementDialog  import ManagementDialog

class ManagementStyleProfiles(ManagementDialog):
    
    def __init__(self, sapCtrl):
        super(ManagementStyleProfiles, self).__init__(controller=sapCtrl)
        self.subphases = []
        self.styles = []

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'managementStyleProfiles.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def setStyles(self, styles):
        self.styles = styles

    def getSubphases(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.subphases
        ]

    def getStyles(self):
        return [
            {
                'name': d['stylename'],
                'value': d['stylename'],
                'data': d
            }
            for d in self.styles
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

    def createCheckBox(self, isChecked):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        checkbox = QtWidgets.QCheckBox('', self.tableWidget)
        checkbox.setChecked(isChecked)
        checkbox.setFixedSize(QtCore.QSize(30, 30))
        checkbox.setIconSize(QtCore.QSize(20, 20))
        layout.addWidget(checkbox)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def addRow(self, profileId, styleName, subphaseId):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(profileId))
        self.tableWidget.setCellWidget(idx, 1, self.createCombobox(idx, 1, self.getStyles(), styleName) )
        self.tableWidget.setCellWidget(idx, 2, self.createCombobox(idx, 2, self.getSubphases(), subphaseId) )

    def addRows(self, profiles):
        self.clearAllItems()
        for profile in profiles:
            self.addRow(
                profile['id'],
                profile['nome'],
                profile['subfase_id']
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
            'nome': self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().itemData(
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
                'nome': row['nome'],
                'subfase_id': row['subfase_id']
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
        self.controller.deleteSapStyleProfiles(rowsIds)

    def openAddForm(self):
        self.controller.addStyleProfile()
    
    def saveTable(self):
        updatedProfiles = self.getUpdatedRows()
        if updatedProfiles:
            self.controller.updateSapStyleProfiles(
                updatedProfiles
            )
        