# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
from .addShortcutForm import AddShortcutForm
import json

class MShortcut(MDialogV2):
    
    def __init__(self, controller, qgis, sap):
        super(MShortcut, self).__init__(controller=controller)
        self.sap = sap
        self.addForm = None
        self.tableWidget.setColumnHidden(5, True)
        self.fetchTableData()

    def fetchTableData(self):
        self.addRows(self.sap.getShortcuts())

    def getColumnsIndexToSearch(self):
        return [0,2,3,4]

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mShortcut.ui'
        )

    def addRows(self, models):
        self.clearAllItems()
        for data in models:
            self.addRow(
                data['id'],
                data['ferramenta'],
                data['idioma'],
                data['atalho'],
                json.dumps(data)
            )
        self.adjustColumns()

    def addRow(self, primaryKey, tool, language, shortcut, dump):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(tool))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(language))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(shortcut))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(dump))
        optionColumn = 1
        self.tableWidget.setCellWidget(
            idx, 
            optionColumn, 
            self.createRowEditWidget(
                self.tableWidget,
                idx, 
                optionColumn, 
                self.handleEditBtn, 
                self.handleDeleteBtn
            )
        )

    def handleEditBtn(self, index):
        data = self.getRowData(index.row())
        self.addForm.close() if self.addForm else None
        self.addForm = AddShortcutForm(
            self.sap,
            self
        )
        self.addForm.activeEditMode(True)
        self.addForm.setData(data)
        self.addForm.accepted.connect(self.fetchTableData)
        self.addForm.show()

    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        message = self.sap.deleteShortcuts([data['id']])
        self.showInfo('Aviso', message)
        self.fetchTableData()

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'ferramenta': self.tableWidget.model().index(rowIndex, 2).data(),
            'idioma': self.tableWidget.model().index(rowIndex, 3).data(),   
            'atalho': self.tableWidget.model().index(rowIndex, 4).data()
        }

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addForm.close() if self.addForm else None
        self.addForm = AddShortcutForm(
            self.sap,
            self
        )
        self.addForm.accepted.connect(self.fetchTableData)
        self.addForm.show()

    @QtCore.pyqtSlot(bool)
    def on_delBtn_clicked(self):
        rowsIds = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rowsIds.append(self.getRowData(qModelIndex.row())['id'])
        if not rowsIds:
            return
        message = self.sap.deleteShortcuts(rowsIds)
        self.showInfo('Aviso', message)
        self.fetchTableData()

        