# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialog  import MDialog

class MEditLayers(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MEditLayers, self).__init__(controller=controller)
        self.tableWidget.setColumnHidden(5, True)
        self.sap = sap
        self.fetchData()

    def fetchData(self):
        self.addRows(self.sap.getLayers())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mEditLayers.ui'
        )

    def getColumnsIndexToSearch(self):
        return list(range(5))

    def addRow(self, layerId, layerName, layerSchema, layerAlias, layerDocumentation, layerInUse):
        idx = self.getRowIndex(layerId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(layerId))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(layerName))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(layerSchema))
        self.tableWidget.setItem(idx, 3, self.createEditableItem(layerAlias))
        self.tableWidget.setItem(idx, 4, self.createEditableItem(layerDocumentation))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(layerInUse))

    def addRows(self, layers):
        self.clearAllItems()
        for layerData in layers:
            self.addRow(
                layerData['id'], 
                layerData['nome'], 
                layerData['schema'],
                layerData['alias'] if 'alias' in layerData else '',
                layerData['documentacao'] if 'documentacao' in layerData else '',
                ('perfil' in layerData and layerData['perfil']) or ( 'atributo' in layerData and layerData['atributo'])
            )
        self.adjustColumns()

    def getRowIndex(self, layerId):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    layerId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'nome': self.tableWidget.model().index(rowIndex, 1).data(),
            'schema': self.tableWidget.model().index(rowIndex, 2).data(),
            'alias': self.tableWidget.model().index(rowIndex, 3).data(),
            'documentacao': self.tableWidget.model().index(rowIndex, 4).data()
        }  

    def saveTable(self):
        message = self.sap.updateLayers(self.getAllTableData())
        self.showInfo('Aviso', message)

    def removeSelected(self):
        deletedLayersIds = []
        ignored = False
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if not ( self.tableWidget.model().index(qModelIndex.row(),5).data() == 'False' ):
                ignored = True
                continue
            deletedLayersIds.append(int(self.tableWidget.model().index(qModelIndex.row(), 0).data()))
            self.tableWidget.removeRow(qModelIndex.row())
        if ignored:
            self.showInfo('Aviso', 'Algumas camadas não serão deletadas, pois estão em uso!')
        if not deletedLayersIds:
            return
        message = self.sap.deleteLayers(deletedLayersIds)
        self.showInfo('Aviso', message)