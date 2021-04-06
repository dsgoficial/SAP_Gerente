# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.managementDialog  import ManagementDialog

class ManagementFmeServers(ManagementDialog):
    
    def __init__(self, sapCtrl):
        super(ManagementFmeServers, self).__init__(controller=sapCtrl)

    def getColumnsIndexToSearch(self):
        return list(range(3))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'managementFmeServers.ui'
        )

    def addRow(self, serverId, serverHost, serverPort):
        idx = self.getRowIndex(serverId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(serverId))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(serverHost))
        self.tableWidget.setItem(idx, 2, self.createEditableItem(serverPort))

    def addRows(self, fmeServers):
        self.clearAllItems()
        for fmeServer in fmeServers:
            self.addRow(
                fmeServer['id'],
                fmeServer['servidor'],
                fmeServer['porta']
            )
        self.adjustColumns()

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
        self.controller.deleteFmeServers(rowsIds)

    def openAddForm(self):
        self.controller.addFmeServer()
    
    def saveTable(self):
        updatedFmeServers = self.getUpdatedRows()
        addedFmeServers = self.getAddedRows()
        if updatedFmeServers:
            self.controller.updateFmeServers(
                updatedFmeServers
            )
        if addedFmeServers:
            self.controller.createFmeServers(
                addedFmeServers
            )
        