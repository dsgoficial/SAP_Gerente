# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialog  import MDialog
from .addFmeProfileForm import AddFmeProfileForm
from .sortComboTableWidgetItem import SortComboTableWidgetItem

class MFmeProfiles(MDialog):
    
    def __init__(self, controller, qgis, sap, fme):
        super(MFmeProfiles, self).__init__(controller=controller)
        self.sap = sap
        self.fme = fme
        self.subphases = []
        self.fmeServers = []
        self.fmeRoutines = []
        self.setFmeServers(self.sap.getFmeServers())
        self.setSubphases(self.sap.getSubphases())
        self.fetchData()
       
    def fetchData(self):
        self.addRows(self.sap.getFmeProfiles())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mFmeProfiles.ui'
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

    def setFmeServers(self, fmeServers):
        self.fmeServers = fmeServers

    def getFmeServers(self):
        return [
            {
                'name': d['servidor'],
                'value': d['id'],
                'data': d
            }
            for d in self.fmeServers
        ]

    def getFmeRoutinesByServerId(self, profileFmeServerId):
        for server in self.getFmeServers():
            if server['data']['id'] == profileFmeServerId:
                return [
                    {
                        'name': routine['rotina'],
                        'value': routine['id']
                    }
                    for routine in self.controller.getFmeRoutines(server['data']['servidor'], server['data']['porta'])
                ]
        return []

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

    def handleServerCombo(self, combo, index):
        serverId = combo.itemData(combo.currentIndex())
        routines = self.getFmeRoutinesByServerId(serverId)
        routines.append({
            'name': '...',
            'value': None
        })
        self.tableWidget.setCellWidget(
            index.row(), 
            2, 
            self.createCombobox(index.row(), 2, routines, None)
        )

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

    def addRow(self, profileId, profileFmeServerId, fmeRoutineId, subphase, completion, falsePositive, order):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(profileId))

        
        self.tableWidget.setItem(idx, 1, SortComboTableWidgetItem())
        self.tableWidget.setCellWidget(idx, 1, self.createCombobox(idx, 1, self.getFmeServers(), profileFmeServerId, self.handleServerCombo))
        
        self.tableWidget.setItem(idx, 2, SortComboTableWidgetItem())
        self.tableWidget.setCellWidget(idx, 2, self.createCombobox(idx, 2, self.getFmeRoutinesByServerId(profileFmeServerId), fmeRoutineId))
        
        self.tableWidget.setCellWidget(idx, 3, self.createCheckBox(completion) )
        
        self.tableWidget.setCellWidget(idx, 4, self.createCheckBox(falsePositive) )
        
        self.tableWidget.setItem(idx, 5, SortComboTableWidgetItem())
        self.tableWidget.setCellWidget(idx, 5, self.createCombobox(idx, 5, self.getSubphases(), subphase))
        
        self.tableWidget.setItem(idx, 6, self.createEditableItem(order))

    def addRows(self, profiles):
        self.clearAllItems()
        for fmeProfile in profiles:
            self.addRow(
                fmeProfile['id'],
                fmeProfile['gerenciador_fme_id'],
                fmeProfile['rotina'],
                fmeProfile['subfase_id'],
                fmeProfile['requisito_finalizacao'],
                fmeProfile['gera_falso_positivo'],
                fmeProfile['ordem']
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
            'gerenciador_fme_id': self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().currentIndex()
            ),
            'rotina': self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().currentIndex()
            ),
            'requisito_finalizacao': self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().isChecked(),
            'gera_falso_positivo': self.tableWidget.cellWidget(rowIndex, 4).layout().itemAt(0).widget().isChecked(),
            'subfase_id': self.tableWidget.cellWidget(rowIndex, 5).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 5).layout().itemAt(0).widget().currentIndex()
            ),
            'ordem': int(self.tableWidget.model().index(rowIndex, 6).data())
        }

    def getAddedRows(self):
        return [
            {
                'gerenciador_fme_id': row['gerenciador_fme_id'],
                'rotina': row['rotina'],
                'requisito_finalizacao': row['requisito_finalizacao'],
                'gera_falso_positivo': row['gera_falso_positivo'],
                'subfase_id': row['subfase_id'],
                'ordem': int(row['ordem'])
            }
            for row in self.getAllTableData()
            if not row['id']
        ]
    
    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'gerenciador_fme_id': row['gerenciador_fme_id'],
                'rotina': row['rotina'],
                'requisito_finalizacao': row['requisito_finalizacao'],
                'gera_falso_positivo': row['gera_falso_positivo'],
                'subfase_id': row['subfase_id'],
                'ordem': int(row['ordem'])
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
        message = self.sap.deleteFmeProfiles(rowsIds)
        self.showInfo('Aviso', message)

    def openAddForm(self):
        self.addFmeProfileForm = AddFmeProfileForm(
            self.sap, 
            self.fme,
            self
        )
        self.addFmeProfileForm.show()
    
    def saveTable(self):
        updatedFmeProfiles = self.getUpdatedRows()
        if not updatedFmeProfiles:
            return
        message = self.sap.updateFmeProfiles(
            updatedFmeProfiles
        )
        self.showInfo('Aviso', message)
      
        