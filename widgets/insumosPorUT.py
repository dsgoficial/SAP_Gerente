# -*- coding: utf-8 -*-
import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidgetAutoComplete import DockWidgetAutoComplete

class InsumosPorUT(DockWidgetAutoComplete):

    def __init__(self, controller, sap):
        super(InsumosPorUT, self).__init__(controller=controller)
        self.sap = sap
        self.tableWidget.setSortingEnabled(True)
        self.setWindowTitle('Insumos por Unidade de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'insumosPorUT.ui'
        )

    def getWorkUnitIds(self):
        return [int(v.strip()) for v in self.workspacesIdLe.text().split(',') if v.strip()]

    def validInput(self):
        return bool(self.workspacesIdLe.text().strip())

    def clearInput(self):
        self.workspacesIdLe.clear()
        self.tableWidget.setRowCount(0)

    def runFunction(self):
        ids = self.getWorkUnitIds()
        if not ids:
            return
        allRows = []
        for utId in ids:
            try:
                data = self.sap.getInsumosPorUT(utId)
                for row in data:
                    row['_ut_id'] = utId
                allRows.extend(data)
            except Exception as e:
                self.showError('Aviso', str(e))
                return
        allRows.sort(key=lambda r: r['_ut_id'])
        self.addRows(allRows)
        if not allRows:
            self.showInfo('Aviso', 'Nenhum insumo associado às unidades de trabalho informadas.')

    def addRows(self, data):
        self.tableWidget.setRowCount(0)
        for row in data:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
            self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(row['unidade_trabalho_id']))
            self.tableWidget.setItem(idx, 1, self.createNotEditableItemNumber(row['insumo_id']))
            self.tableWidget.setItem(idx, 2, self.createNotEditableItem(row['nome']))
            self.tableWidget.setItem(idx, 3, self.createNotEditableItem(row['caminho']))
            self.tableWidget.setItem(idx, 4, self.createNotEditableItem(row.get('caminho_padrao', '')))
            self.tableWidget.setItem(idx, 5, self.createNotEditableItem(str(row['epsg']) if row.get('epsg') else ''))
            self.tableWidget.setItem(idx, 6, self.createNotEditableItem(row.get('tipo_insumo', '')))
            self.tableWidget.setItem(idx, 7, self.createNotEditableItem(row.get('grupo_insumo', '')))
        self.tableWidget.resizeColumnsToContents()

    def createNotEditableItem(self, value):
        item = QtWidgets.QTableWidgetItem(str(value) if value is not None else '')
        item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)
        return item

    def createNotEditableItemNumber(self, value):
        item = QtWidgets.QTableWidgetItem()
        item.setData(QtCore.Qt.ItemDataRole.DisplayRole, value)
        item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)
        return item

    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('insumosPorUT', 'workUnit')
        self.workspacesIdLe.setText(values)

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Informe ao menos um ID de unidade de trabalho.')
            return
        self.runFunction()
