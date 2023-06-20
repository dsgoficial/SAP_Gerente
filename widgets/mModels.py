# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addModelForm import AddModelForm

class MModels(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MModels, self).__init__(controller=controller)
        self.sap = sap
        self.addModelForm = None
        self.tableWidget.setColumnHidden(2, True)
        self.tableWidget.setColumnHidden(4, True)
        self.fetchTableData()

    def fetchTableData(self):
        self.addRows(self.sap.getModels())

    def getColumnsIndexToSearch(self):
        return list(range(2))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mModels.ui'
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

        uploadBtn = self.createTableToolButton( 'Carregar modelo', self.getUploadIconPath() )
        uploadBtn.clicked.connect(
            lambda *args, index=index: self.handleLoadModelBtn(index)
        )
        layout.addWidget(uploadBtn)

        downloadBtn = self.createTableToolButton( 'Baixar modelo', self.getDownloadIconPath() )
        downloadBtn.clicked.connect(
            lambda *args, index=index: self.handleDownloadModelBtn(index)
        )
        layout.addWidget(downloadBtn)

        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def handleLoadModelBtn(self, index):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   'Carregar Arquivo',
                                                   '',
                                                  '*.model3')
        if not filePath[0]:
            return
        with open(filePath[0], 'r') as f:
            data = f.read()
        self.tableWidget.setItem(index.row(), 2, self.createNotEditableItem(data) )
        self.saveTable()
        #self.showInfo('Aviso', "Modelo carregado com sucesso!")

    def handleDownloadModelBtn(self, index):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                   'Salvar Arquivo',
                                                   "modelo",
                                                  '*.model3')
        if not filePath[0]:
            return
        with open(filePath[0], 'w') as f:
            f.write( self.tableWidget.model().index( index.row(), 2 ).data() )
        self.showInfo('Aviso', "Modelo salvo com sucesso!")

    def addRow(self, modelId, modelName, modelDescription, modelXml):
        idx = self.getRowIndex(modelName)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createEditableItem(modelName))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(modelDescription))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(modelXml))
        self.tableWidget.setCellWidget(idx, 3, self.createEditModelWidget(idx, 3) )
        self.tableWidget.setItem(idx, 4, self.createNotEditableItemNumber(modelId))

    def addRows(self, models):
        self.clearAllItems()
        for modelData in models:
            self.addRow(
                modelData['id'],
                modelData['nome'],
                modelData['descricao'],
                modelData['model_xml'],
            )
        self.adjustColumns()

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
            'nome': self.tableWidget.model().index(rowIndex, 0).data(),
            'descricao': self.tableWidget.model().index(rowIndex, 1).data(),
            'model_xml': self.tableWidget.model().index(rowIndex, 2).data(),
            'id': self.tableWidget.model().index(rowIndex, 4).data()
        }

    def openAddForm(self):
        self.addModelForm.close() if self.addModelForm else None
        self.addModelForm = AddModelForm(
            self.sap,
            self
        )
        self.addModelForm.save.connect(self.fetchTableData)
        self.addModelForm.show()
    
    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'nome': row['nome'],
                'descricao': row['descricao'],
                'model_xml': row['model_xml'],
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
        message = self.sap.deleteModels(rowsIds)
        self.showInfo('Aviso', message)
    
    def saveTable(self):
        updatedProfiles = self.getUpdatedRows()
        if not updatedProfiles:
            return
        message = self.sap.updateModels(
            updatedProfiles
        )
        self.showInfo('Aviso', message)