# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.managementDialog  import ManagementDialog

class ManagementStyles(ManagementDialog):
    
    def __init__(self, sapCtrl):
        super(ManagementStyles, self).__init__(controller=sapCtrl)
        self.tableWidget.setColumnHidden(3, True)
        self.tableWidget.setColumnHidden(4, True)
        self.tableWidget.setColumnHidden(5, True)
        self.tableWidget.setColumnHidden(6, True)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'managementStyles.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return list(range(3))

    def addRow(self, schemaName, layerName, styleName, qmlStyle, sldStyle, ui, geometryColumn):
        idx = self.getRowIndex(schemaName, layerName, styleName)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createEditableItem(schemaName))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(layerName))
        self.tableWidget.setItem(idx, 2, self.createEditableItem(styleName))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(qmlStyle))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(sldStyle))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(ui))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(geometryColumn))

    def addRows(self, styles):
        self.clearAllItems()
        for styleData in styles:
            self.addRow(
                styleData['f_table_schema'],
                styleData['f_table_name'],
                styleData['stylename'],
                styleData['styleqml'],
                styleData['stylesld'],
                styleData['ui'],
                styleData['f_geometry_column']
            )
        self.adjustColumns()

    def getRowIndex(self, schemaName, layerName, styleName):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    schemaName == self.tableWidget.model().index(idx, 0).data()
                    and
                    layerName == self.tableWidget.model().index(idx, 1).data()
                    and
                    styleName == self.tableWidget.model().index(idx, 2).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'f_table_schema': self.tableWidget.model().index(rowIndex, 0).data(),
            'f_table_name': self.tableWidget.model().index(rowIndex, 1).data(),
            'stylename': self.tableWidget.model().index(rowIndex, 2).data(),
            'styleqml': self.tableWidget.model().index(rowIndex, 3).data(),
            'stylesld': self.tableWidget.model().index(rowIndex, 4).data(),
            'ui': '' if self.tableWidget.model().index(rowIndex, 5).data() == None else self.tableWidget.model().index(rowIndex, 5).data(),
            'f_geometry_column': self.tableWidget.model().index(rowIndex, 6).data()
        }

    def openAddForm(self):
        self.controller.loadStylesFromLayersSelection()
    
    @QtCore.pyqtSlot(bool)
    def on_loadBtn_clicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.controller.applyStylesOnLayers(
            self.getSelectedRowData()
        )
        QtWidgets.QApplication.restoreOverrideCursor()

    def getAddedRows(self):
        return [
            {
                'f_table_schema': row['f_table_schema'],
                'f_table_name': row['f_table_name'],
                'stylename': row['stylename'],
                'styleqml': row['styleqml'],
                'stylesld': row['stylesld'],
                'ui': row['ui'],
                'f_geometry_column': row['f_geometry_column']
            }
            for row in self.getAllTableData()
            if not row['id']
        ]
    
    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'f_table_schema': row['f_table_schema'],
                'f_table_name': row['f_table_name'],
                'stylename': row['stylename'],
                'styleqml': row['styleqml'],
                'stylesld': row['stylesld'],
                'ui': row['ui'],
                'f_geometry_column': row['f_geometry_column']
            }
            for row in self.getAllTableData()
            if row['id']
        ]

    def removeSelected(self):
        rowsIds = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rowsIds.append(int(self.getRowData(qModelIndex.row())['id']))
            self.tableWidget.removeRow(qModelIndex.row())
        self.controller.deleteSapStyles(rowsIds)
    
    def saveTable(self):
        updated = self.getUpdatedRows()
        added = self.getAddedRows()
        if updated:
            self.controller.updateSapStyles(
                updated
            )
        if added:
            self.controller.createSapStyles(
                added
            )