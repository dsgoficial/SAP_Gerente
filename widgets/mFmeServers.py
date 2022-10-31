# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog

class MFmeServers(MDialog):
    
    def __init__(self, sapCtrl):
        super(MFmeServers, self).__init__(controller=sapCtrl)

    def getColumnsIndexToSearch(self):
        return list(range(3))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mFmeServers.ui'
        )

    def addRow(self, serverId, serverUrl):
        idx = self.getRowIndex(serverId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(serverId))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(serverUrl))

    def addRows(self, fmeServers):
        self.clearAllItems()
        for fmeServer in fmeServers:
            self.addRow(
                fmeServer['id'],
                fmeServer['url']
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
            'url': self.tableWidget.model().index(rowIndex, 1).data(),
        }

    def getAddedRows(self):
        return [
            {
                'url': row['url']
            }
            for row in self.getAllTableData()
            if not row['id']
        ]
    
    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'url': row['url']
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
        if updatedFmeServers:
            self.controller.updateFmeServers(
                updatedFmeServers
            )
        