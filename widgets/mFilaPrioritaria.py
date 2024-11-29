# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
from .addFilaPrioritariaForm import AddFilaPrioritariaForm
import json

class MFilaPrioritaria(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addProjectForm=AddFilaPrioritariaForm
            ):
        super(MFilaPrioritaria, self).__init__(controller=controller)
        self.addProjectForm = addProjectForm
        self.qgis = qgis
        self.sap = sap
        self.addProjectFormDlg = None
        self.tableWidget.setColumnHidden(8, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mFilaPrioritaria.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getFilaPrioritaria()
        self.addRows(data)

    def addRows(self, data):
        self.clearAllItems()
        for d in data:
            self.addRow(
                d['id'],
                d['lote'],
                d['bloco'],
                d['subfase'],
                d['atividade_id'],
                d['usuario'],
                d['prioridade'],
                json.dumps(d)
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            lote,
            bloco,
            subfase,
            atividade_id,
            usuario,
            prioridade,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setCellWidget(idx, 2, self.createLabelV2(lote, idx, 2))
        self.tableWidget.setCellWidget(idx, 3, self.createLabelV2(bloco, idx, 3))
        self.tableWidget.setCellWidget(idx, 4, self.createLabelV2(subfase, idx, 4))
        self.tableWidget.setCellWidget(idx, 5, self.createLabelV2(str(atividade_id), idx, 5))
        self.tableWidget.setCellWidget(idx, 6, self.createLabelV2(usuario, idx, 6))
        self.tableWidget.setCellWidget(idx, 7, self.createLabelV2(str(prioridade), idx, 7))
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

    def createRowEditWidget(self, 
            tableWidget, 
            row, 
            col, 
            editCallback, 
            deleteCallback
        ):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        index = QtCore.QPersistentModelIndex(tableWidget.model().index(row, col))

        # editBtn = self.createToolButton( tableWidget, 'Editar', self.getEditIconPath() )
        # editBtn.clicked.connect(
        #     lambda *args, index=index: editCallback(index)
        # )
        # layout.addWidget(editBtn)

        deleteBtn = self.createToolButton( tableWidget, 'Deletar', self.getDeleteIconPath() )
        deleteBtn.clicked.connect(
            lambda *args, index=index: deleteCallback(index)
        )
        layout.addWidget(deleteBtn)

        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd
    
    def handleEditBtn(self, index):
        data = self.getRowData(index.row())
        self.addProjectFormDlg.close() if self.addProjectFormDlg else None
        self.addProjectFormDlg = self.addProjectForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addProjectFormDlg.activeEditMode(True)
        self.addProjectFormDlg.setData(data)
        self.addProjectFormDlg.save.connect(self.fetchData)
        self.addProjectFormDlg.show()

        
    def handleDeleteBtn(self, index):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir a fila prioritária?')
        if not result:
            return
        data = self.getRowData(index.row())
        message = self.sap.deleteFilaPrioritaria([data['id']])
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
        data = json.loads(self.tableWidget.model().index(rowIndex, 8).data())
        return {
            'id': data['id']
        }