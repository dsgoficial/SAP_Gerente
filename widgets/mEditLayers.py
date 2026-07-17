# -*- coding: utf-8 -*-
import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV3 import MDialogV3

class MEditLayers(MDialogV3):
    
    def __init__(self, controller, qgis, sap):
        super(MEditLayers, self).__init__(controller=controller)
        self.sap = sap
        self.fetchData()

    def fetchData(self):
        self.addRows(self.getLayersWithProductionLines())

    def getLayersWithProductionLines(self):
        layers = self.sap.getLayers()
        productionLinesByLayerId = {
            row['camada_id']: row['linhas_producao']
            for row in self.sap.getLayersProductionLines()
        }
        for layer in layers:
            layer['linhas_producao'] = productionLinesByLayerId.get(layer['id'], '')
        return layers

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mEditLayers.ui'
        )

    def getColumnsIndexToSearch(self):
        return list(range(4))

    def addRow(self, layerId, layerName, layerSchema, layerProductionLine, layerInUse):
        idx = self.getRowIndex(layerId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        idItem = self.createNotEditableItemNumber(layerId)
        idItem.setData(QtCore.Qt.ItemDataRole.UserRole, bool(layerInUse))
        self.tableWidget.setItem(idx, 0, idItem)
        self.tableWidget.setItem(idx, 1, self.createEditableItem(layerName))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(layerSchema))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(layerProductionLine))

    def addRows(self, layers):
        self.clearAllItems()
        for layerData in layers:
            productionLines = layerData['linhas_producao'] if 'linhas_producao' in layerData else ''
            self.addRow(
                layerData['id'],
                layerData['nome'],
                layerData['schema'],
                '\n'.join(productionLines.split(', ')) if productionLines else '',
                ('perfil' in layerData and layerData['perfil']) or ( 'atributo' in layerData and layerData['atributo'])
            )
        self.adjustTable()

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
            'schema': self.tableWidget.model().index(rowIndex, 2).data()
        }

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        self.saveTable()

    def saveTable(self):
        message = self.sap.updateLayers(self.getAllTableData())
        message and self.showInfo('Aviso', message)

    @QtCore.pyqtSlot(bool)
    def on_delBtn_clicked(self):
        self.removeSelected()

    def removeSelected(self):
        deletedLayersIds = []
        ignored = False
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            inUse = self.tableWidget.item(qModelIndex.row(), 0).data(QtCore.Qt.ItemDataRole.UserRole)
            if inUse:
                ignored = True
                continue
            deletedLayersIds.append(int(self.tableWidget.model().index(qModelIndex.row(), 0).data()))
            self.tableWidget.removeRow(qModelIndex.row())
        if ignored:
            self.showInfo('Aviso', 'Algumas camadas não serão deletadas, pois estão em uso!')
        if not deletedLayersIds:
            return
        message = self.sap.deleteLayers(deletedLayersIds)
        message and self.showInfo('Aviso', message)