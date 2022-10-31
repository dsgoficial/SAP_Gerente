# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog

class MModelProfiles(MDialog):
    
    def __init__(self, sapCtrl):
        super(MModelProfiles, self).__init__(controller=sapCtrl)
        self.subphases = []
        self.models = []
        self.routines = []
        self.lots = []

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mModelProfiles.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def setModels(self, models):
        self.models = models

    def setRoutines(self, routines):
        self.routines = routines

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

    def getModels(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.models
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

    def getRoutines(self):
        return [
            {
                'name': d['nome'],
                'value': d['code'],
                'data': d
            }
            for d in self.routines
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

    def addRow(self, profileId, modelId, subphaseId, loteId, routineId, completion, order, parameters):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(profileId))
        self.tableWidget.setCellWidget(idx, 1, self.createCombobox(idx, 1, self.getModels(), modelId) )
        self.tableWidget.setCellWidget(idx, 2, self.createCheckBox(completion) )
        self.tableWidget.setCellWidget(idx, 3, self.createCombobox(idx, 3, self.getLots(), loteId) )
        self.tableWidget.setCellWidget(idx, 4, self.createCombobox(idx, 4, self.getRoutines(), routineId) )
        self.tableWidget.setCellWidget(idx, 5, self.createCombobox(idx, 5, self.getSubphases(), subphaseId) )
        self.tableWidget.setItem(idx, 6, self.createEditableItem(order))
        self.tableWidget.setItem(idx, 7, self.createEditableItem(parameters))

    def addRows(self, profiles):
        self.clearAllItems()
        for modelProfile in profiles:
            self.addRow(
                modelProfile['id'],
                modelProfile['qgis_model_id'],
                modelProfile['subfase_id'],
                modelProfile['lote_id'],
                modelProfile['tipo_rotina_id'],
                modelProfile['requisito_finalizacao'],
                modelProfile['ordem'],
                modelProfile['parametros']
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
            'qgis_model_id': self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().currentIndex()
            ),
            'requisito_finalizacao': self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().isChecked(),
            'lote_id': self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().currentIndex()
            ),
            'tipo_rotina_id': self.tableWidget.cellWidget(rowIndex, 4).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 4).layout().itemAt(0).widget().currentIndex()
            ),
            'subfase_id': self.tableWidget.cellWidget(rowIndex, 5).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 5).layout().itemAt(0).widget().currentIndex()
            ),
            'ordem': int(self.tableWidget.model().index(rowIndex, 6).data()),
            'parametros': self.tableWidget.model().index(rowIndex, 7).data()
        }

    def getUpdatedRows(self):
        return [
             {
                'id': int(row['id']),
                'qgis_model_id': row['qgis_model_id'],
                'requisito_finalizacao': row['requisito_finalizacao'],
                'subfase_id': row['subfase_id'],
                'tipo_rotina_id': row['tipo_rotina_id'],
                'lote_id': row['lote_id'],
                'ordem': int(row['ordem']),
                'parametros': row['parametros']
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
        self.controller.deleteSapModelProfiles(rowsIds)

    def openAddForm(self):
        self.controller.addModelProfile()
    
    def saveTable(self):
        updatedFmeProfiles = self.getUpdatedRows()
        if updatedFmeProfiles:
            self.controller.updateSapModelProfiles(
                updatedFmeProfiles
            )
        