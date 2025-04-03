import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2 import MDialogV2
from .addCampo import AdicionarCampo
import json

class MFields(MDialogV2):
    
    def __init__(self, controller, qgis, sap):
        super(MFields, self).__init__(controller=controller)
        self.qgis = qgis
        self.sap = sap
        self.adicionarCampoDlg = None
        self.tableWidget.setColumnHidden(8, True)
        self.tableWidget.setColumnHidden(0, True)
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
        self.addRows(data)

    def format_categories(self, categories_str):
        if not categories_str:
            return ""
        if categories_str.startswith('{') and categories_str.endswith('}'):
            categories_str = categories_str[1:-1]
        categories_str = categories_str.replace('"', '')
        categories_str = categories_str.replace(',', ', ')
        while '  ' in categories_str:
            categories_str = categories_str.replace('  ', ' ')
        return categories_str

    def addRows(self, campos):
        self.clearAllItems()
        for campo in campos:
            formatted_categories = self.format_categories(campo['categorias'])
            self.addRow(
                campo['id'],
                campo['nome'],
                campo['descricao'],
                campo['orgao'],
                campo['situacao'],
                campo['pit'],
                formatted_categories,
                json.dumps(campo)
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            name,
            description,
            orgao,
            situacao,
            pit,
            categorias,
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
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(pit))
        self.tableWidget.setItem(idx, 7, self.createNotEditableItem(categorias))
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
        campo_data = self.getRowData(index.row())
        self.adicionarCampoDlg = AdicionarCampo(self.controller, self.sap, self.qgis, campo_data)
        self.adicionarCampoDlg.finished.connect(self.fetchData)
        self.adicionarCampoDlg.show()
        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        qtd_fotos = int(data['qtd_fotos']) if data['qtd_fotos'] is not None else 0
        qtd_track = int(data['qtd_track']) if data['qtd_track'] is not None else 0
        if qtd_fotos != 0 or qtd_track != 0:
            message = self.showInfo('Aviso', 'Esse campo possui fotos e/ou trackers associados. Para deletar o Campo, delete as informações associadas primeiro.')
        else:
            result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir o campo?')
            if not result:
                return
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
        data = json.loads(self.tableWidget.model().index(rowIndex, 8).data())
        return data

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.adicionarCampoDlg = AdicionarCampo(self.controller, self.sap, self.qgis)
        self.adicionarCampoDlg.finished.connect(self.fetchData)
        self.adicionarCampoDlg.show()