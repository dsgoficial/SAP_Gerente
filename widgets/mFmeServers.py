# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialog  import MDialog
from .addFmeServerForm import AddFmeServerForm

class MFmeServers(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MFmeServers, self).__init__(controller=controller)
        self.sap = sap
        self.fetchData()
        self.addFmeServerForm = None

    def fetchData(self):
        self.addRows(self.sap.getFmeServers())

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
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(serverId))
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
        message = self.sap.deleteFmeServers(rowsIds)
        self.showInfo('Aviso', message)

    def openAddForm(self):
        self.addFmeServerForm.close() if self.addFmeServerForm  else None
        self.addFmeServerForm = AddFmeServerForm(
            self.sap,
            self
        )
        self.addFmeServerForm.accepted.connect(self.fetchData)
        self.addFmeServerForm.show()

    def saveTable(self):
        updatedFmeServers = self.getUpdatedRows()
        if not updatedFmeServers:
            return
        message = self.sap.updateFmeServers(
            updatedFmeServers
        )
        self.showInfo('Aviso', message)
        