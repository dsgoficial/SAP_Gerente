# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
from .addLineageForm import AddLineageForm
import json

class MLineage(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                AddLineageForm=AddLineageForm
            ):
        super(MLineage, self).__init__(controller=controller)
        self.addLineageForm = AddLineageForm
        self.qgis = qgis
        self.sap = sap
        self.addLineageFormDlg = None
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(5, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mLineage.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getLineages()
        self.addRows(data)

    def addRows(self, data):
        self.clearAllItems()
        subphases = self.sap.getSubphases()
        lots = self.sap.getLots()
        for row in data:
            lot = next(filter(lambda item: item['id'] == row['lote_id'], lots), None)
            subphase = next(filter(lambda item: item['subfase_id'] == row['subfase_id'], subphases), None) 
            self.addRow(
                row['id'],
                lot['nome_abrev'],
                "{} - {}".format(
                    subphase['fase'],
                    subphase['subfase']
                ), 
                row['tipo_exibicao'],
                json.dumps(row)
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            loteName,
            subphaseName,
            showTypeName,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setCellWidget(idx, 2, self.createLabelV2(loteName, idx, 2))
        self.tableWidget.setCellWidget(idx, 3, self.createLabelV2(subphaseName, idx, 3))
        self.tableWidget.setCellWidget(idx, 4, self.createLabelV2(showTypeName, idx, 4))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(dump))

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
        self.addLineageFormDlg.close() if self.addLineageFormDlg else None
        self.addLineageFormDlg = self.addLineageForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addLineageFormDlg.activeEditMode(True)
        self.addLineageFormDlg.setData(data)
        self.addLineageFormDlg.save.connect(self.fetchData)
        self.addLineageFormDlg.show()

    def handleDeleteBtn(self, index):
        """ result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir ?')
        if not result:
            return """
        data = self.getRowData(index.row())
        message = self.sap.deleteLineages([data['id']])
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
        return json.loads(self.tableWidget.model().index(rowIndex, 5).data())

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addLineageFormDlg.close() if self.addLineageFormDlg else None
        self.addLineageFormDlg = self.addLineageForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addLineageFormDlg.save.connect(self.fetchData)
        self.addLineageFormDlg.show()