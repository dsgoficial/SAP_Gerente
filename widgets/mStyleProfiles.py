# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
from .addStyleProfileForm import AddStyleProfileForm
from .addStyleProfileLotForm import AddStyleProfileLotForm

class MStyleProfiles(MDialogV2):
    
    def __init__(self, controller, qgis, sap):
        super(MStyleProfiles, self).__init__(controller=controller)
        self.sap = sap
        self.qgis = qgis
        self.addStyleProfileForm = None
        self.addStyleProfileLotForm = None
        self.subphases = []
        self.styles = []
        self.lots = []
        self.setSubphases(self.sap.getSubphases())
        self.setStyles(self.sap.getGroupStyles())
        self.setLots(self.sap.getLots())
        self.updateTable()

    def updateTable(self):
        self.addRows(self.sap.getStyleProfiles())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mStyleProfiles.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def setStyles(self, styles):
        self.styles = styles

    def setLots(self, lots):
        self.lots = lots

    def getSubphases(self):
        return [
            {
                'name': d['subfase'],
                'value': d['subfase_id'],
                'data': d
            }
            for d in self.subphases
        ]

    def getStyles(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.styles
        ]

    def getLots(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.lots
        ]

    def createCheckBox(self, isChecked):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        checkbox = QtWidgets.QCheckBox('', self.tableWidget)
        checkbox.setChecked(isChecked)
        checkbox.setFixedSize(QtCore.QSize(30, 30))
        checkbox.setIconSize(QtCore.QSize(20, 20))
        layout.addWidget(checkbox)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def addRow(self, profileId, groupStyleId, subphaseId, loteId):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(profileId))
        self.tableWidget.setCellWidget(idx, 1, self.createComboboxV2(idx, 1, self.getLots(), loteId) )

        
        subphases = [ s for s in self.subphases if s['lote_id'] == loteId ]
        subphases.sort(key=lambda item: int(item['subfase_id']), reverse=True) 
        self.tableWidget.setCellWidget(idx, 2, self.createComboboxV2(
                idx, 
                2, 
                [
                   {
                        'name': d['subfase'],
                        'value': d['subfase_id'],
                        'data': d
                    } for d in subphases
                ], 
                subphaseId
            ) 
        )

        self.tableWidget.setCellWidget(idx, 3, self.createComboboxV2(idx, 3, self.getStyles(), groupStyleId) )

    def addRows(self, profiles):
        self.clearAllItems()
        for profile in profiles:
            self.addRow(
                profile['id'],
                profile['grupo_estilo_id'],
                profile['subfase_id'],
                profile['lote_id']
            )
        self.adjustColumns()

    def getRowIndex(self, profileId):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    profileId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        styleWd = self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget()
        subPhaseWd = self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget()
        lotWd = self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget()
        return {
            'id': self.tableWidget.model().index(rowIndex, 0).data(),
            'grupo_estilo_id': styleWd.itemData(styleWd.currentIndex()),
            'subfase_id': subPhaseWd.itemData(subPhaseWd.currentIndex()),
            'lote_id': lotWd.itemData(lotWd.currentIndex())
        }
    
    def getUpdatedRows(self):
        return [
             {
                'id': int(row['id']),
                'grupo_estilo_id': row['grupo_estilo_id'],
                'subfase_id': row['subfase_id'],
                'lote_id': row['lote_id']
            }
            for row in self.getAllTableData()
            if row['id']
        ]

    @QtCore.pyqtSlot(bool)
    def on_delBtn_clicked(self):
        rowsIds = []
        while self.tableWidget.selectionModel().selectedRows():
            qModelIndex = self.tableWidget.selectionModel().selectedRows()[0]
            if self.getRowData(qModelIndex.row())['id']:
                rowsIds.append(int(self.getRowData(qModelIndex.row())['id']))
                self.tableWidget.removeRow(qModelIndex.row())
        if not rowsIds:
            return
        self.deleteSapStyleProfiles(rowsIds)

    def deleteSapStyleProfiles(self, ids):
        message = self.sap.deleteStyleProfiles(ids)
        message and self.showInfo('Aviso', message)
        self.updateTable()

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addStyleProfileForm.close() if self.addStyleProfileForm else None
        self.addStyleProfileForm = AddStyleProfileForm(
            self.controller, 
            self.qgis, 
            self.sap,
            self
        )
        self.addStyleProfileForm.save.connect(self.updateTable)
        self.addStyleProfileForm.show()

    @QtCore.pyqtSlot(bool)
    def on_copyBtn_clicked(self):
        if not self.getSelected():
            self.showInfo('Aviso', 'Selecione as linhas!')
            return
        self.addStyleProfileLotForm.close() if self.addStyleProfileLotForm else None
        self.addStyleProfileLotForm = AddStyleProfileLotForm(
            self.controller, 
            self.qgis, 
            self.sap,
            self.getSelected(),
            self
        )
        self.addStyleProfileLotForm.save.connect(self.updateTable)
        self.addStyleProfileLotForm.show()

    def getSelected(self):
        rows = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rows.append(self.getRowData(qModelIndex.row()))
        return rows

    def saveTable(self):
        updatedProfiles = self.getUpdatedRows()
        if updatedProfiles:
            self.sap.updateStyleProfiles(
                updatedProfiles
            )
        
    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        self.saveTable()
        self.showInfo('Aviso', 'Atualizado com sucesso!')