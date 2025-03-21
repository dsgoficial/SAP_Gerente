# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2 import MDialogV2
from .addCampo import AdicionarCampo
import json

class MFields(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap
            ):
        super(MFields, self).__init__(controller=controller)
        self.qgis = qgis
        self.sap = sap
        self.adicionarCampoDlg = None
        self.tableWidget.setColumnHidden(6, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mFields.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getCampos()
        print(data)
        self.addRows(data)

    def addRows(self, campos):
        self.clearAllItems()
        for campo in campos:
            self.addRow(
                campo['id'],
                campo['nome'],
                campo['descricao'],
                campo['orgao'],
                campo['situacao'],
                json.dumps(campo)
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            name,
            description,
            orgao,
            situacao,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setCellWidget(idx, 2, self.createLabelV2(name, idx, 2))
        self.tableWidget.setCellWidget(idx, 3, self.createLabelV2(description, idx, 3))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(orgao))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(situacao))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(dump))
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
        # A edição de campos existentes pode precisar de uma implementação diferente
        # dependendo de como sua AdicionarCampo pode ou não suportar a edição
        data = self.getRowData(index.row())
        self.showInfo('Aviso', 'Funcionalidade de edição em desenvolvimento')
        
    def handleDeleteBtn(self, index):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir o campo?')
        if not result:
            return
        data = self.getRowData(index.row())
        message = self.sap.deletaCampo(data['id'])
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
        data = json.loads(self.tableWidget.model().index(rowIndex, 6).data())
        return data

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        # Abre a janela existente AdicionarCampo
        self.adicionarCampoDlg = AdicionarCampo(self.controller, self.sap, self.qgis)
        # Você pode adicionar um evento para atualizar a tabela após adicionar um campo
        self.adicionarCampoDlg.finished.connect(self.fetchData)
        self.adicionarCampoDlg.show()