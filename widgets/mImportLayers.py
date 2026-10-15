# -*- coding: utf-8 -*-
import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialog  import MDialog
from SAP_Gerente.modules.sap.api.contrato import rotuloDadoProducao

class MImportLayers(MDialog):
    
    def __init__(self, sapCtrl):
        super(MImportLayers, self).__init__(controller=sapCtrl)
        # Toda produção é base versionada (2.4.0): a lista é a das bases
        # versionadas (dado de produção tipo 4), e as camadas são os datasets
        # do repositório, lidos do serviço pelo repasse do SAP, sem conexão
        # PostGIS. As conexões PostgreSQL salvas no QGIS não entram mais.
        self.databases = self.basesVersionadas()
        self.loadDatabases(self.databases)

    def basesVersionadas(self):
        bases = []
        for d in self.controller.getSapBasesVersionadas():
            if not d.get('configuracao_producao'):
                continue
            bases.append({
                'alias': rotuloDadoProducao(d),
                'repo_id': d['configuracao_producao']
            })
        return bases
        
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
        self.databasesCb.addItems(['...'] + [ d['alias'] for d in self.databases])

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
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
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
            # SAP 3.0: a camada é só (schema, nome); o validador recusa chave a mais.
            layersImported.append({
                'nome': rowData['nome'],
                'schema': rowData['schema']
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
            self.getLayersImported(),
            parent=self
        )
        # Recarrega a lista: a camada importada sai dela.
        dbData = self.getDatabaseData(self.getCurrentDatabase())
        if not ( dbData is None ):
            self.loadMImportLayers(dbData)

    def getDatabaseData(self, dbAlias):
        for dbData in self.getDatabases():
            if not ( dbData['alias'] == dbAlias ):
                continue
            return dbData
    
    @QtCore.pyqtSlot(str)
    def on_databasesCb_currentTextChanged(self, dbName):
        self.clearAllItems()
        dbData = self.getDatabaseData(dbName)
        if dbData is None:
            return
        self.loadMImportLayers(dbData)
        self.setCheckedAllLayers(self.selectAllCkb.checkState())

    def loadMImportLayers(self, dbData):
        baseLayers = self.controller.getLayersFromVersionamento(dbData['repo_id'], parent=self)
        layersRows = []
        sapLayers = self.controller.getSapLayers(parent=self)
        sapLayersNames = [ (d['schema'], d['nome']) for d in sapLayers ]
        for layerData in baseLayers:
            if (layerData['schema'], layerData['nome']) in sapLayersNames:
                continue
            layersRows.append({
                'nome' : layerData['nome'],
                'schema' : layerData['schema'],
                'alias' : '',
                'documentacao' : ''
                
            })
        self.addRows(layersRows)

    @QtCore.pyqtSlot(int)
    def on_selectAllCkb_stateChanged(self, state):
        self.setCheckedAllLayers(state)

    def setCheckedAllLayers(self, state):
        for idx in range(self.tableWidget.rowCount()):
            self.tableWidget.cellWidget(idx, 0).layout().itemAt(0).widget().setCheckState(state)
