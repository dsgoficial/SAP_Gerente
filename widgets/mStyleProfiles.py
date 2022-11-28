# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addStyleProfileForm import AddStyleProfileForm

class MStyleProfiles(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MStyleProfiles, self).__init__(controller=controller)
        self.sap = sap
        self.qgis = qgis
        self.addStyleProfileForm = None
        self.subphases = []
        self.styles = []
        self.lots = []
        self.setSubphases(self.sap.getSubphases())
        self.setStyles(self.sap.getGroupStyles())
        self.setLots(self.sap.getLots())
        self.updateTable()

    def updateTable(self):
        self.addRows(self.sap.getStyleProfiles())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mStyleProfiles.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def setStyles(self, styles):
        self.styles = styles

    def setLots(self, lots):
        self.lots = lots

    def getSubphases(self):
        return [
            {
                'name': d['subfase'],
                'value': d['subfase_id'],
                'data': d
            }
            for d in self.subphases
        ]

    def getStyles(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.styles
        ]

    def getLots(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.lots
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

    def addRow(self, profileId, groupStyleId, subphaseId, loteId):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(profileId))
        self.tableWidget.setCellWidget(idx, 1, self.createCombobox(idx, 1, self.getStyles(), groupStyleId) )
        self.tableWidget.setCellWidget(idx, 2, self.createCombobox(idx, 2, self.getSubphases(), subphaseId) )
        self.tableWidget.setCellWidget(idx, 3, self.createCombobox(idx, 3, self.getLots(), loteId) )

    def addRows(self, profiles):
        self.clearAllItems()
        for profile in profiles:
            self.addRow(
                profile['id'],
                profile['grupo_estilo_id'],
                profile['subfase_id'],
                profile['lote_id']
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
        styleWd = self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget()
        subPhaseWd = self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget()
        lotWd = self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget()
        return {
            'id': self.tableWidget.model().index(rowIndex, 0).data(),
            'grupo_estilo_id': styleWd.itemData(styleWd.currentIndex()),
            'subfase_id': subPhaseWd.itemData(subPhaseWd.currentIndex()),
            'lote_id': lotWd.itemData(lotWd.currentIndex())
        }
    
    def getUpdatedRows(self):
        return [
             {
                'id': int(row['id']),
                'grupo_estilo_id': row['grupo_estilo_id'],
                'subfase_id': row['subfase_id'],
                'lote_id': row['lote_id']
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
        self.addStyleProfileForm.close() if self.addStyleProfileForm else None
        self.addStyleProfileForm = AddStyleProfileForm(
            self.controller, 
            self.qgis, 
            self.sap,
            self
        )
        self.addStyleProfileForm.save.connect(self.updateTable)
        self.addStyleProfileForm.show()
    
    def saveTable(self):
        updatedProfiles = self.getUpdatedRows()
        if updatedProfiles:
            self.sap.updateStyleProfiles(
                updatedProfiles
            )
        