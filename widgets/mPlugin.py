# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addPluginForm import AddPluginForm

class MPlugin(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MPlugin, self).__init__(controller=controller)
        self.sap = sap
        self.addForm = None
        self.tableWidget.setColumnHidden(2, True)
        # self.tableWidget.setColumnHidden(4, True)
        self.fetchTableData()

    def fetchTableData(self):
        print(self.sap.getPlugins())
        #self.addRows(self.sap.getAlias())

    def getColumnsIndexToSearch(self):
        return list(range(2))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mPlugin.ui'
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

    def createEditModelWidget(self, row, col):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, col))

        editBtn = self.createTableToolButton( 'Editar', self.getEditIconPath() )
        editBtn.clicked.connect(
            lambda *args, index=index: self.handleEditBtn(index)
        )
        layout.addWidget(editBtn)

        uploadBtn = self.createTableToolButton( 'Carregar Alias', self.getUploadIconPath() )
        uploadBtn.clicked.connect(
            lambda *args, index=index: self.handleLoadAliasBtn(index)
        )
        layout.addWidget(uploadBtn)

        downloadBtn = self.createTableToolButton( 'Baixar Alias', self.getDownloadIconPath() )
        downloadBtn.clicked.connect(
            lambda *args, index=index: self.handleDownloadAliasBtn(index)
        )
        layout.addWidget(downloadBtn)

        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def handleEditBtn(self, index):
        data = self.getRowData(index.row())
        self.addForm.close() if self.addForm else None
        self.addForm = AddPluginForm(
            self.sap,
            self
        )
        self.addForm.activeEditMode(True)
        self.addForm.setData(data)
        self.addForm.accepted.connect(self.fetchTableData)
        self.addForm.show()

    def handleLoadAliasBtn(self, index):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   'Carregar Arquivo',
                                                   '',
                                                  '*.json')
        if not filePath[0]:
            return
        with open(filePath[0], 'r') as f:
            data = f.read()
        self.tableWidget.setItem(index.row(), 2, self.createNotEditableItem(data) )
        self.showInfo('Aviso', "Alias carregado com sucesso!")

    def handleDownloadAliasBtn(self, index):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                   'Salvar Arquivo',
                                                   "alias",
                                                  '*.json')
        if not filePath[0]:
            return
        with open(filePath[0], 'w') as f:
            f.write( self.tableWidget.model().index( index.row(), 2 ).data() )
        self.showInfo('Aviso', "Alias salvo com sucesso!")

    def addRows(self, models):
        self.clearAllItems()
        for modelData in models:
            self.addRow(
                modelData['id'],
                modelData['nome'],
                modelData['definicao_alias']
            )
        self.adjustColumns()

    def addRow(self, modelId, modelName, aliasJSON):
        idx = self.getRowIndex(modelName)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(modelId))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(modelName))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(aliasJSON))
        self.tableWidget.setCellWidget(idx, 3, self.createEditModelWidget(idx, 3) )

    def getRowIndex(self, modelName):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    modelName == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'id': self.tableWidget.model().index(rowIndex, 0).data(),
            'nome': self.tableWidget.model().index(rowIndex, 1).data(),
            'definicao_alias': self.tableWidget.model().index(rowIndex, 2).data(),   
        }

    def openAddForm(self):
        self.addForm.close() if self.addForm else None
        self.addForm = AddPluginForm(
            self.sap,
            self
        )
        self.addForm.accepted.connect(self.fetchTableData)
        self.addForm.show()
    
    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'nome': row['nome'],
                'definicao_alias': row['definicao_alias']
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
        message = self.sap.deleteAlias(rowsIds)
        self.showInfo('Aviso', message)
    
    def saveTable(self):
        updatedProfiles = self.getUpdatedRows()
        if not updatedProfiles:
            return
        message = self.sap.updateAlias(
            updatedProfiles
        )
        self.showInfo('Aviso', message)