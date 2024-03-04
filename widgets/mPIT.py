# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
from .addPIT import AddPIT
import json

class MPIT(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addProjectForm=AddPIT
            ):
        super(MPIT, self).__init__(controller=controller)
        self.addProjectForm = addProjectForm
        self.qgis = qgis
        self.sap = sap
        self.addProjectFormDlg = None
        self.tableWidget.setColumnHidden(5, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mPIT.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getPITs()
        self.addRows(data)

    def addRows(self, data):
        self.clearAllItems()
        for d in data:
            print(d)
            self.addRow(
                d['id'],
                d['ano'],
                d['lote'],
                d['meta'],
                json.dumps(d)
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            ano,
            lote,
            meta,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setCellWidget(idx, 2, self.createLabelV2(str(ano), idx, 2))
        self.tableWidget.setCellWidget(idx, 3, self.createLabelV2(lote, idx, 3))
        self.tableWidget.setCellWidget(idx, 4, self.createLabelV2(str(meta), idx, 4))
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
        self.addProjectFormDlg.close() if self.addProjectFormDlg else None
        self.addProjectFormDlg = self.addProjectForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addProjectFormDlg.activeEditMode(True)
        self.addProjectFormDlg.setData(data)
        self.addProjectFormDlg.save.connect(self.fetchData)
        self.addProjectFormDlg.show()

        
    def handleDeleteBtn(self, index):
        # result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir o PIT?')
        # if not result:
        #     return
        data = self.getRowData(index.row())
        message = self.sap.deletePITs([data['id']])
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
        data = json.loads(self.tableWidget.model().index(rowIndex, 5).data())
        return {
            'id': data['id'],
            'ano': data['ano'],
            'meta': data['meta'],
            'lote_id': data['lote_id']
        }

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addProjectFormDlg.close() if self.addProjectFormDlg else None
        self.addProjectFormDlg = self.addProjectForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addProjectFormDlg.save.connect(self.fetchData)
        self.addProjectFormDlg.show()