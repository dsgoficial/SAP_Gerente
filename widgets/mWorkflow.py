# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addWorkflowForm import AddWorkflowForm

class MWorkflow(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MWorkflow, self).__init__(controller=controller)
        self.sap = sap
        self.addForm = None
        self.tableWidget.setColumnHidden(2, True)
        self.tableWidget.setColumnHidden(4, True)
        self.fetchTableData()

    def fetchTableData(self):
        self.addRows(self.sap.getWorkflows())

    def getColumnsIndexToSearch(self):
        return list(range(2))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mWorkflow.ui'
        )

    def getUploadIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'upload.png'
        )

    def getDownloadIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'download.png'
        )

    def createEditWidget(self, row, col):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, col))

        uploadBtn = self.createTableToolButton( 'Carregar workflow', self.getUploadIconPath() )
        uploadBtn.clicked.connect(
            lambda *args, index=index: self.handleLoadBtn(index)
        )
        layout.addWidget(uploadBtn)

        downloadBtn = self.createTableToolButton( 'Baixar workflow', self.getDownloadIconPath() )
        downloadBtn.clicked.connect(
            lambda *args, index=index: self.handleDownloadBtn(index)
        )
        layout.addWidget(downloadBtn)

        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def handleLoadBtn(self, index):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   'Carregar Arquivo',
                                                   '',
                                                  '*.json')
        if not filePath[0]:
            return
        with open(filePath[0], 'r') as f:
            data = f.read()
        self.tableWidget.setItem(index.row(), 2, self.createNotEditableItem(data) )
        self.saveTable()

    def handleDownloadBtn(self, index):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                   'Salvar Arquivo',
                                                   "workflow",
                                                  '*.json')
        if not filePath[0]:
            return
        with open(filePath[0], 'w') as f:
            f.write( self.tableWidget.model().index( index.row(), 2 ).data() )
        self.showInfo('Aviso', "Modelo salvo com sucesso!")

    def addRow(self, primaryKey, name, description, workflow):
        idx = self.getRowIndex(name)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createEditableItem(name))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(description))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(workflow))
        self.tableWidget.setCellWidget(idx, 3, self.createEditWidget(idx, 3) )
        self.tableWidget.setItem(idx, 4, self.createNotEditableItemNumber(primaryKey))

    def addRows(self, models):
        self.clearAllItems()
        for modelData in models:
            self.addRow(
                modelData['id'],
                modelData['nome'],
                modelData['descricao'],
                modelData['workflow_json'],
            )
        self.adjustColumns()

    def getRowIndex(self, name):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    name == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'nome': self.tableWidget.model().index(rowIndex, 0).data(),
            'descricao': self.tableWidget.model().index(rowIndex, 1).data(),
            'workflow_json': self.tableWidget.model().index(rowIndex, 2).data(),
            'id': self.tableWidget.model().index(rowIndex, 4).data()
        }

    def openAddForm(self):
        self.addForm.close() if self.addForm else None
        self.addForm = AddWorkflowForm(
            self.sap,
            self
        )
        self.addForm.save.connect(self.fetchTableData)
        self.addForm.show()
    
    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'nome': row['nome'],
                'descricao': row['descricao'],
                'workflow_json': row['workflow_json'],
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
        message = self.sap.deleteWorkflows(rowsIds)
        self.showInfo('Aviso', message)
    
    def saveTable(self):
        updated = self.getUpdatedRows()
        if not updated:
            return
        message = self.sap.updateWorkflows(
            updated
        )
        self.showInfo('Aviso', message)