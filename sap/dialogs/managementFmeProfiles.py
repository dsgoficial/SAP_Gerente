# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.sap.dialogs.managementDialog  import ManagementDialog

class ManagementFmeProfiles(ManagementDialog):
    
    def __init__(self, sapCtrl):
        super(ManagementFmeProfiles, self).__init__(sapCtrl=sapCtrl)
        self.subphases = []
        self.servers = []
        self.routines = []
        
    def getColumnsIndexToSearch(self):
        return list(range(3))

    def setSubphases(self, subphases):
        self.subphases = []

    def getSubphases(self):
        return self.subphases

    def setServers(self, servers):
        self.servers = servers

    def getServers(self):
        return self.servers

    def setRoutines(self, routines):
        self.routines = routines

    def getRoutines(self):
        return self.routines

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'managementFmeProfiles.ui'
        )

    def addRow(self, profileId, profileFmeServerId, fmeRoutineId, subphase, completion, falsePositive):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(profileId))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(profileFmeServerId))
        self.tableWidget.setItem(idx, 2, self.createEditableItem(fmeRoutineId))
        self.tableWidget.setItem(idx, 3, self.createEditableItem(subphase))
        self.tableWidget.setItem(idx, 4, self.createEditableItem(completion))
        self.tableWidget.setItem(idx, 5, self.createEditableItem(falsePositive))

    def addRows(self, profiles):
        for fmeProfile in profiles:
            self.addRow(
                fmeProfile['id'],
                fmeProfile['gerenciador_fme_id'],
                fmeProfile['rotina'],
                fmeProfile['requisito_finalizacao'],
                fmeProfile['gera_falso_positivo'],
                fmeProfile['subfase_id']
            )

    def getRowIndex(self, serverId):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    serverId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'id': self.tableWidget.model().index(rowIndex, 0).data(),
            'servidor': self.tableWidget.model().index(rowIndex, 1).data(),
            'porta': self.tableWidget.model().index(rowIndex, 2).data()
        }

    def getAddedRows(self):
        return [
            {
                'servidor': row['servidor'],
                'porta': row['porta']
            }
            for row in self.getAllTableData()
            if not row['id']
        ]
    
    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'servidor': row['servidor'],
                'porta': row['porta']
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
        self.sapCtrl.deleteFmeServers(rowsIds)

    def openAddForm(self):
        self.sapCtrl.addFmeProfile()
    
    def saveTable(self):
        updatedFmeServers = self.getUpdatedRows()
        addedFmeServers = self.getAddedRows()
        if updatedFmeServers:
            self.sapCtrl.updateFmeServers(
                updatedFmeServers
            )
        if addedFmeServers:
            self.sapCtrl.createFmeServers(
                addedFmeServers
            )
        