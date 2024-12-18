# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2 import MDialogV2
from .addLPForm import AddLPForm
from .addProductionLine import AddProductionLine
import json

class EditProductionLine(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addLPForm=AddLPForm,
                addProductionLine=AddProductionLine
            ):
        super(EditProductionLine, self).__init__(controller=controller)
        self.addLPForm = addLPForm
        self.addProductionLine = addProductionLine
        self.qgis = qgis
        self.sap = sap
        self.setWindowTitle('Linha de Produção')
        self.addLPFormDlg = None
        self.addProductionLineDlg = None
        self.tableWidget.setColumnHidden(7, True)  # Hide dump column
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'editProductionLine.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2, 3, 4, 5]  # Adjusted column indices for search

    def fetchData(self):
        data = self.sap.getProductionLines()
        self.addRows(data)

    def addRows(self, data):
        self.clearAllItems()
        for row in data:
            self.addRow(
                row['linha_producao_id'],
                row['linha_producao'],
                row['linha_producao_abrev'],
                row['tipo_produto'],
                row['descricao'],
                row['disponivel'],
                json.dumps(row)
            )
        self.adjustColumns()

    def addRow(self, 
            primaryKey, 
            nome,
            abrev,
            tipo_produto,
            descricao,
            disponivel,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        
        # Create edit button in second column (index 1)
        editButton = QtWidgets.QPushButton('', self.tableWidget)
        editButton.setIcon(QtGui.QIcon(self.getEditIconPath()))
        editButton.clicked.connect(lambda: self.handleEditBtn(self.tableWidget.model().index(idx, 1)))
        editButton.setFixedWidth(25)
        self.tableWidget.setCellWidget(idx, 1, editButton)
        
        # Set other columns
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(nome))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(abrev))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(tipo_produto))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(descricao))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem('Sim' if disponivel else 'Não'))
        self.tableWidget.setItem(idx, 7, self.createNotEditableItem(dump))

    def handleEditBtn(self, index):
        data = self.getRowData(index.row())
        self.addLPFormDlg.close() if self.addLPFormDlg else None
        self.addLPFormDlg = self.addLPForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addLPFormDlg.activeEditMode(True)
        self.addLPFormDlg.setData(data)
        self.addLPFormDlg.save.connect(self.fetchData)
        self.addLPFormDlg.show()

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return json.loads(self.tableWidget.model().index(rowIndex, 7).data())

    @QtCore.pyqtSlot(bool)
    def on_addBtn_clicked(self):
        self.addProductionLineDlg.close() if self.addProductionLineDlg else None
        self.addProductionLineDlg = self.addProductionLine(
            self.controller,
            self.qgis,
            self.sap,
            self
        )
        self.addProductionLineDlg.accepted.connect(self.fetchData)
        self.addProductionLineDlg.show()