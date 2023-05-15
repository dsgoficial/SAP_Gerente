# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2
from .addLotForm import AddLotForm
import json

class MLots(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addLotForm=AddLotForm
            ):
        super(MLots, self).__init__(controller=controller)
        self.addLotForm = addLotForm
        self.qgis = qgis
        self.sap = sap
        self.addLotFormDlg = None
        self.tableWidget.setColumnHidden(8, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mLots.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getLots()
        self.addRows(data)

    def addRows(self, data):
        productionLines = self.sap.getProductionLines()
        projects = self.sap.getProjects()
        self.clearAllItems()
        for row in data:
            productionLine = next(filter(lambda item: item['linha_producao_id'] == row['linha_producao_id'], productionLines), None)
            project = next(filter(lambda item: item['id'] == row['projeto_id'], projects), None)
            self.addRow(
                row['id'],
                row['nome'],
                row['descricao'],
                row['nome_abrev'],
                row['denominador_escala'],
                productionLine['linha_producao'],
                project['nome'],
                json.dumps(row)
            )
        self.adjustColumns()

    def addRow(self, 
            primaryKey, 
            name,
            description,
            alias,
            scale,
            productionLine,
            project,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        self.tableWidget.setCellWidget(idx, 2, self.createLabel(name))
        self.tableWidget.setCellWidget(idx, 3, self.createLabel(description))
        self.tableWidget.setCellWidget(idx, 4, self.createLabel(alias))
        self.tableWidget.setCellWidget(idx, 5, self.createLabel(str(scale)))
        self.tableWidget.setCellWidget(idx, 6, self.createLabel(project))
        self.tableWidget.setCellWidget(idx, 7, self.createLabel(productionLine))
        self.tableWidget.setItem(idx, 8, self.createNotEditableItem(dump))
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
        self.addLotFormDlg.close() if self.addLotFormDlg else None
        self.addLotFormDlg = self.addLotForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addLotFormDlg.activeEditMode(True)
        self.addLotFormDlg.setData(data)
        self.addLotFormDlg.save.connect(self.fetchData)
        self.addLotFormDlg.show()

        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        message = self.sap.deleteLots([data['id']])
        self.showInfo('Aviso', message)
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
        return json.loads(self.tableWidget.model().index(rowIndex, 8).data())

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addLotFormDlg.close() if self.addLotFormDlg else None
        self.addLotFormDlg = self.addLotForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addLotFormDlg.save.connect(self.fetchData)
        self.addLotFormDlg.show()