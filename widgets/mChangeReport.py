# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2
from .addChangeReport import AddChangeReport
import time

class MChangeReport(MDialogV2):
    
    def __init__(self, controller, qgis, sap):
        super(MChangeReport, self).__init__(controller=controller)
        self.sap = sap
        self.addForm = None
        self.fetchTableData()

    def fetchTableData(self):
        self.addRows(self.sap.getChangeReport())

    def addRows(self, data):
        self.clearAllItems()
        for d in data:
            self.addRow(
                d['id'],
                d['data'],
                d['descricao']
            )
        self.adjustColumns()

    def addRow(self, primaryKey, date, description):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(date))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(description))
        self.tableWidget.setCellWidget(idx, 1, self.createRowEditWidget(
            self.tableWidget, 
            idx, 
            1, 
            self.handleEditBtn, 
            self.handleDeleteBtn
        ) )

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getColumnsIndexToSearch(self):
        return [0,2,3]

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mChangeReport.ui'
        )

    def handleEditBtn(self, index):
        data = self.getRowData(index.row())
        self.addForm.close() if self.addForm else None
        self.addForm = AddChangeReport(
            self.sap,
            self
        )
        self.addForm.activeEditMode(True)
        self.addForm.setData(data)
        self.addForm.accepted.connect(self.fetchTableData)
        self.addForm.show()

    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        try:
            message = self.sap.deleteChangeReport([data['id']])
            self.showInfo('Aviso', message)
            self.fetchTableData()
        except Exception as e:
            self.showError('Aviso', str(e))
            return ''  

    def getRowData(self, rowIndex):
        return {
            'id': self.tableWidget.model().index(rowIndex, 0).data(),
            'data': self.tableWidget.model().index(rowIndex, 2).data(),
            'descricao': self.tableWidget.model().index(rowIndex, 3).data(),   
        }

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addForm.close() if self.addForm else None
        self.addForm = AddChangeReport(
            self.sap,
            self
        )
        self.addForm.accepted.connect(self.fetchTableData)
        self.addForm.show()