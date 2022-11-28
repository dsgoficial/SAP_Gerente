# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2
from .addStyleForm import AddStyleForm

class MStyles(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addStyleForm=AddStyleForm
            ):
        super(MStyles, self).__init__(controller=controller)
        self.addStyleForm = addStyleForm
        self.qgis = qgis
        self.sap = sap
        self.addStyleFormDlg = None
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(5, True)
        self.tableWidget.setColumnHidden(6, True)
        self.tableWidget.setColumnHidden(7, True)
        self.tableWidget.setColumnHidden(8, True)
        self.tableWidget.setColumnHidden(9, True)
        self.addRows( self.sap.getStyles() )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mStyles.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return list(range(3))

    def fetchData(self):
        data = self.sap.getStyles()
        self.addRows(data)

    def addRows(self, styles):
        self.clearAllItems()
        for styleData in styles:
            self.addRow(
                styleData['id'],
                styleData['f_table_schema'],
                styleData['f_table_name'],
                styleData['stylename'],
                styleData['styleqml'],
                styleData['stylesld'],
                styleData['ui'],
                styleData['f_geometry_column'],
                styleData['grupo_estilo_id']
            )
        self.adjustColumns()

    def addRow(self, 
            primaryKey, 
            schemaName, 
            layerName, 
            styleName, 
            qmlStyle, 
            sldStyle, 
            ui, 
            geometryColumn,
            groupStyleId
        ):
        idx = self.getRowIndex(schemaName, layerName, styleName)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(schemaName))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(layerName))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(styleName))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(qmlStyle))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(sldStyle))
        self.tableWidget.setItem(idx, 7, self.createNotEditableItem(ui))
        self.tableWidget.setItem(idx, 8, self.createNotEditableItem(geometryColumn))
        self.tableWidget.setItem(idx, 9, self.createNotEditableItem(groupStyleId))
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
        self.addStyleFormDlg.close() if self.addStyleFormDlg else None
        self.addStyleFormDlg = self.addStyleForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addStyleFormDlg.loadGroupStyles(
            self.sap.getGroupStyles()
        )
        self.addStyleFormDlg.activeEditMode(True)
        self.addStyleFormDlg.setLayerWidgetVisible(True)
        self.addStyleFormDlg.setData(data)
        self.addStyleFormDlg.save.connect(self.fetchData)
        self.addStyleFormDlg.show()

        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        message = self.sap.deleteStyles([data['id']])
        self.showInfo('Aviso', message)
        self.fetchData()

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
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'f_table_schema': self.tableWidget.model().index(rowIndex, 2).data(),
            'f_table_name': self.tableWidget.model().index(rowIndex, 3).data(),
            'stylename': self.tableWidget.model().index(rowIndex, 4).data(),
            'styleqml': self.tableWidget.model().index(rowIndex, 5).data(),
            'stylesld': self.tableWidget.model().index(rowIndex, 6).data(),
            'ui': '' if self.tableWidget.model().index(rowIndex, 7).data() == None else self.tableWidget.model().index(rowIndex, 7).data(),
            'f_geometry_column': self.tableWidget.model().index(rowIndex, 8).data(),
            'grupo_estilo_id': int(self.tableWidget.model().index(rowIndex, 9).data())
        }

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        stylesData = self.qgis.getQmlStyleFromLayersTreeSelection()
        if len(stylesData) == 0:
            self.showError('Aviso', "Selecione no mínimo uma camada.")
            return
        self.addStyleFormDlg.close() if self.addStyleFormDlg else None
        self.addStyleFormDlg = self.addStyleForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addStyleFormDlg.loadGroupStyles(
            self.sap.getGroupStyles()
        )
        self.addStyleFormDlg.setStylesData(stylesData)
        self.addStyleFormDlg.save.connect(self.fetchData)
        self.addStyleFormDlg.show()
    
    @QtCore.pyqtSlot(bool)
    def on_loadBtn_clicked(self):
        style = self.getSelectedRowData()
        if not style:
            self.showError('Erro', 'Selecione um estilo!')
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.controller.applyStylesOnLayers(style)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
    
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
                'f_geometry_column': row['f_geometry_column'],
                'grupo_estilo_id': row['grupo_estilo_id']
            }
            for row in self.getAllTableData()
            if row['id']
        ]

    @QtCore.pyqtSlot(bool)
    def on_delBtn_clicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.removeSelected()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def removeSelected(self):
        rowsIds = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            data =self.getRowData(qModelIndex.row())
            rowsIds.append(int(data['id']))
            self.tableWidget.removeRow(qModelIndex.row())
        message = self.sap.deleteStyles(rowsIds)
        self.showInfo('Aviso', message)
    
    def saveTable(self):
        updated = self.getUpdatedRows()
        if updated:
            self.controller.updateSapStyles(
                updated
            )