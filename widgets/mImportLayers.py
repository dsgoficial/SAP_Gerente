# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog

class MImportLayers(MDialog):
    
    def __init__(self, sapCtrl):
        super(MImportLayers, self).__init__(controller=sapCtrl)
        self.databases = self.controller.getSapDatabases()
        self.loadDatabases(self.databases)
        
    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mImportLayers.ui'
        )

    def loadDatabases(self, databases):
        self.databases = databases
        self.databasesCb.clear()
        self.databasesCb.addItems(['...'] + [ d['nome'] for d in self.databases])

    def getDatabases(self):
        return self.databases

    def getCurrentDatabase(self):
        return self.databasesCb.currentText()
    
    def getColumnsIndexToSearch(self):
        return [1,2,3]

    def createCheckBox(self, isChecked):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        checkbox = QtWidgets.QCheckBox('', self.tableWidget)
        checkbox.setChecked(isChecked)
        checkbox.setFixedSize(QtCore.QSize(30, 30))
        checkbox.setIconSize(QtCore.QSize(20, 20))
        layout.addWidget(checkbox)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def addRow(self, layerName, layerSchema, layerAlias, layerDocumentation):
        idx = self.tableWidget.rowCount()
        self.tableWidget.insertRow(idx)
        self.tableWidget.setCellWidget(idx, 0, self.createCheckBox(False))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(layerName))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(layerSchema))
        self.tableWidget.setItem(idx, 3, self.createEditableItem(layerAlias))
        self.tableWidget.setItem(idx, 4, self.createEditableItem(layerDocumentation))

    def addRows(self, layers):
        self.clearAllItems()
        for layerData in layers:
            self.addRow(
                layerData['nome'],
                layerData['schema'],
                layerData['alias'],
                layerData['documentacao']
            )
        self.adjustColumns()

    def getRowIndex(self):
        pass

    def getRowData(self, rowIndex):
        return {
            'imported': self.tableWidget.cellWidget(rowIndex, 0).layout().itemAt(0).widget().isChecked(),
            'nome': self.tableWidget.model().index(rowIndex, 1).data(),
            'schema': self.tableWidget.model().index(rowIndex, 2).data(),
            'alias': self.tableWidget.model().index(rowIndex, 3).data(),
            'documentacao': self.tableWidget.model().index(rowIndex, 4).data()
        }

    def getLayersImported(self):
        layersImported = []
        for rowData in self.getAllTableData():
            if not rowData['imported']:
                continue
            layersImported.append({
                'nome': rowData['nome'],
                'schema': rowData['schema'],
                'alias': rowData['alias'],
                'documentacao': rowData['documentacao']
            })
        return layersImported        

    def saveTable(self):
        if not self.getLayersImported():
            self.showInfo(
                'Aviso',
                'Não há camadas selecionadas!'
            )
            return
        self.controller.importLayers(
            self.getLayersImported()
        )

    def getDatabaseData(self, dbName):
        for dbData in self.getDatabases():
            if not ( dbData['nome'] == dbName ):
                continue
            return dbData
    
    @QtCore.pyqtSlot(str)
    def on_databasesCb_currentTextChanged(self, dbName):
        self.clearAllItems()
        dbData = self.getDatabaseData(dbName)
        if dbData is None:
            return
        self.controller.loadManagementImportLayers(
            dbData['servidor'],
            dbData['porta'],
            dbData['nome']
        )