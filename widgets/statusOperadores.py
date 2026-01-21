# -*- coding: utf-8 -*-
import os
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory


class StatusOperadores(QtWidgets.QDialog):

    def __init__(self, controller, qgis, sap,
                 messageFactory=UtilsFactory().createMessageFactory()):
        super(StatusOperadores, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.controller = controller
        self.sap = sap
        self.messageFactory = messageFactory
        self.setWindowTitle('Status dos Operadores')
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.horizontalHeader().setSectionsClickable(False)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.refreshBtn.clicked.connect(self.fetchData)
        self.searchLe.textEdited.connect(self.searchRows)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'statusOperadores.ui'
        )

    def getColumnsIndexToSearch(self):
        return list(range(6))

    def fetchData(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            data = self.sap.getResumoUsuario()
            self.addRows(data)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def sortData(self, data):
        postoOrder = {}
        for d in data:
            posto = d.get('nome_abrev', 'N/A')
            if posto not in postoOrder:
                postoOrder[posto] = len(postoOrder)

        def sortKey(item):
            posto = item.get('nome_abrev', 'N/A')
            status = item.get('status_usuario', '')
            statusIdx = 1 if status == 'Ocioso' else 0
            postoIdx = postoOrder.get(posto, 999)
            return (statusIdx, postoIdx)

        return sorted(data, key=sortKey)

    def addRows(self, data):
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setRowCount(0)
        sortedData = self.sortData(data)
        for d in sortedData:
            self.addRow(
                d.get('nome_abrev', 'N/A'),
                d.get('nome_usuario', 'N/A'),
                d.get('status_usuario', 'N/A'),
                d.get('nome_subfase', 'N/A'),
                d.get('nome_lote', 'N/A'),
                d.get('nome_bloco', 'N/A')
            )
        self.tableWidget.resizeColumnsToContents()

    def addRow(self, postoGrad, operador, status, subfase, lote, bloco):
        idx = self.tableWidget.rowCount()
        self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(postoGrad))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(operador))

        statusItem = self.createNotEditableItem(status)
        if status == 'Em Atividade':
            statusItem.setBackground(QtGui.QColor(144, 238, 144))
        else:
            statusItem.setBackground(QtGui.QColor(255, 200, 200))
        self.tableWidget.setItem(idx, 2, statusItem)

        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(subfase))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(lote))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(bloco))

    def createNotEditableItem(self, value):
        item = QtWidgets.QTableWidgetItem('' if value is None else str(value))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        return item

    def searchRows(self, text):
        for idx in range(self.tableWidget.rowCount()):
            if text and not self.hasTextOnRow(idx, text):
                self.tableWidget.setRowHidden(idx, True)
            else:
                self.tableWidget.setRowHidden(idx, False)

    def hasTextOnRow(self, rowIdx, text):
        for colIdx in self.getColumnsIndexToSearch():
            cellText = self.tableWidget.model().index(rowIdx, colIdx).data()
            if cellText and text.lower() in cellText.lower():
                return True
        return False
