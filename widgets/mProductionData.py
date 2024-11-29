# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
from .addProductionDataForm import AddProductionDataForm
import json

class MProductionData(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addProductionDataForm=AddProductionDataForm
            ):
        super(MProductionData, self).__init__(controller=controller)
        self.addProductionDataForm = addProductionDataForm
        self.qgis = qgis
        self.sap = sap
        self.setWindowTitle('Configurações de Conexão')
        self.addProductionDataFormDlg = None
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(4, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mProductionData.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getProductionData()
        self.addRows(data)

    def addRows(self, data):
        self.clearAllItems()
        for row in data:
            self.addRow(
                row['id'],
                row['tipo_dado_producao'],
                row['configuracao_producao'],
                json.dumps(row)
            )
        self.adjustColumns()

    def addRow(self, 
            primaryKey, 
            productionDataType,
            productionSetup,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(productionDataType))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(productionSetup))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(dump))
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
        self.addProductionDataFormDlg.close() if self.addProductionDataFormDlg else None
        self.addProductionDataFormDlg = self.addProductionDataForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addProductionDataFormDlg.activeEditMode(True)
        self.addProductionDataFormDlg.setData(data)
        self.addProductionDataFormDlg.save.connect(self.fetchData)
        self.addProductionDataFormDlg.show()

        
    def handleDeleteBtn(self, index):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir o dado de produção?')
        if not result:
            return
        data = self.getRowData(index.row())
        message = self.sap.deleteProductionData([data['id']])
        message and self.showInfo('Aviso', message)
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
        return json.loads(self.tableWidget.model().index(rowIndex, 4).data())

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addProductionDataFormDlg.close() if self.addProductionDataFormDlg else None
        self.addProductionDataFormDlg = self.addProductionDataForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addProductionDataFormDlg.save.connect(self.fetchData)
        self.addProductionDataFormDlg.show()