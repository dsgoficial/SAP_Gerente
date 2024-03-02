# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
from .addBlockForm import AddBlockForm
import json

class MBlocks(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addBlockForm=AddBlockForm
            ):
        super(MBlocks, self).__init__(controller=controller)
        self.addBlockForm = addBlockForm
        self.qgis = qgis
        self.sap = sap
        self.setWindowTitle('Blocos')
        self.addBlockFormDlg = None
        self.tableWidget.setColumnHidden(5, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mBlocks.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getBlocks()
        self.addRows(data)

    def addRows(self, data):
        lots = self.sap.getLots()
        self.clearAllItems()
        for row in data:
            lot = next(filter(lambda item: item['id'] == row['lote_id'], lots), None)
            self.addRow(
                row['id'],
                row['nome'],
                row['prioridade'],
                lot['nome'],
                json.dumps(row)
            )
        self.adjustColumns()

    def addRow(self, 
            primaryKey, 
            name,
            lotName,
            priority,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(name))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(priority))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItemNumber(lotName))
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
        self.addBlockFormDlg.close() if self.addBlockFormDlg else None
        self.addBlockFormDlg = self.addBlockForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addBlockFormDlg.activeEditMode(True)
        self.addBlockFormDlg.setData(data)
        self.addBlockFormDlg.save.connect(self.fetchData)
        self.addBlockFormDlg.show()

        
    def handleDeleteBtn(self, index):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir o bloco?')
        if not result:
            return
        data = self.getRowData(index.row())
        message = self.sap.deleteBlocks([data['id']])
        self.showInfo('Aviso', message)
        self.fetchData()

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return json.loads(self.tableWidget.model().index(rowIndex, 5).data())

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addBlockFormDlg.close() if self.addBlockFormDlg else None
        self.addBlockFormDlg = self.addBlockForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addBlockFormDlg.save.connect(self.fetchData)
        self.addBlockFormDlg.show()