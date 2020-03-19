# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.sap.dialogs.managementDialog  import ManagementDialog

class ManagementModels(ManagementDialog):
    
    def __init__(self, sapCtrl):
        super(ManagementModels, self).__init__(sapCtrl=sapCtrl)
        self.tableWidget.setColumnHidden(2, True)

    def getColumnsIndexToSearch(self):
        return list(range(2))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'managementModels.ui'
        )

    def getUploadIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'upload.png'
        )

    def createUploadModelBtn(self, row, col):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        button = QtWidgets.QPushButton('', self.tableWidget)
        button.setIcon(QtGui.QIcon(self.getUploadIconPath()))
        button.setFixedSize(QtCore.QSize(30, 30))
        button.setIconSize(QtCore.QSize(20, 20))
        index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, col))
        button.clicked.connect(
            lambda *args, index=index: self.handleLoadModelBtn(index)
        )
        layout.addWidget(button)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def handleLoadModelBtn(self, index):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.model3')
        if not filePath[0]:
            return
        with open(filePath[0], 'r') as f:
            data = f.read()
        self.tableWidget.setItem(index.row(), 2, self.createNotEditableItem(data) )
        self.showInfo('Aviso', "Modelo carregado com sucesso!")

    def addRow(self, modelName, modelDescription, modelXml):
        idx = self.getRowIndex(modelName)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createEditableItem(modelName))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(modelDescription))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(modelXml))
        self.tableWidget.setCellWidget(idx, 3, self.createUploadModelBtn(idx, 3) )

    def addRows(self, models):
        self.clearAllItems()
        for modelData in models:
            self.addRow(
                modelData['nome'],
                modelData['descricao'],
                modelData['model_xml']
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
            'model_xml': self.tableWidget.model().index(rowIndex, 2).data()
        }

    def openAddForm(self):
        self.sapCtrl.addModel()
    
    def saveTable(self):
        self.sapCtrl.updateSapModels(
            self.getAllTableData()
        )