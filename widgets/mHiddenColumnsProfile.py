# -*- coding: utf-8 -*-
import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialog  import MDialog
from .addHiddenColumnsProfileForm import AddHiddenColumnsProfileForm
from .addHiddenColumnsProfileLotForm import AddHiddenColumnsProfileLotForm
from .sortComboTableWidgetItem import SortComboTableWidgetItem
import json

class MHiddenColumnsProfile(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MHiddenColumnsProfile, self).__init__(controller=controller)
        self.tableWidget.setColumnHidden(4, True)
        self.groupData = {}
        self.sap = sap
        self.lots = []
        self.subphases = []
        self.columnSets = []
        self.addHiddenColumnsProfileForm = None
        self.addHiddenColumnsProfileLotForm = None
        self.setSubphases(self.sap.getSubphases())
        self.setHiddenColumns(self.sap.getHiddenColumns())
        self.setLots(self.sap.getAllLots())
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mHiddenColumnsProfile.ui'
        )

    def getColumnsIndexToSearch(self):
        return [0,1]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def getSubphases(self):
        return [
            {
                'name': d['subfase'],
                'value': d['subfase_id'],
                'data': d
            }
            for d in self.subphases
        ]

    def setLots(self, lots):
        self.lots = lots

    def getLots(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.lots
        ]

    def setHiddenColumns(self, columnSets):
        self.columnSets = columnSets

    def getHiddenColumns(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.columnSets
        ]

    

    def createCheckBox(self, isChecked):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        checkbox = QtWidgets.QCheckBox('', self.tableWidget)
        checkbox.setChecked(isChecked)
        checkbox.setFixedSize(QtCore.QSize(30, 30))
        checkbox.setIconSize(QtCore.QSize(20, 20))
        layout.addWidget(checkbox)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def createOptionWidget(self, row):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        for button in self.getRowOptionSetup(row):
            btn = self.createTableToolButton(button['tooltip'], button['iconPath'] )
            btn.clicked.connect(button['callback'])
            layout.addWidget(btn)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def getRowOptionSetup(self, row):
        return [
            {
                'tooltip': 'Editar',
                'iconPath': self.getEditIconPath(),
                'callback': lambda b, row=row: self.handleEdit(row) 
            },
            {
                'tooltip': 'Excluir',
                'iconPath': self.getTrashIconPath(),
                'callback': lambda b, row=row: self.handleDelete(row) 
            }
        ]

    def handleDelete(self, row):
        try:
            message = self.sap.deleteHiddenColumnsProfile([
                int(self.getRowData(row)['id'])
            ])
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            self.fetchData()

    def fetchData(self):
        self.addRows(self.sap.getHiddenColumnsProfile())

    def addRows(self, data):
        self.clearAllItems()
        for d in data:  
            self.addRow(
                str(d['id']), 
                d['colunas_ocultas'], 
                d['subfase_id'], 
                d['lote_id'], 
                d['colunas_ocultas_id'],
                json.dumps(d)
            )
        self.adjustColumns()

    def addRow(self, 
            relId, 
            columnSet,
            subphaseId,
            lotId,
            columnSetId, 
            dump
        ):
        idx = self.getRowIndex(relId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(relId))

        self.tableWidget.setCellWidget(idx, 1, self.createComboboxV2(idx, 1, self.getLots(), lotId) )
        
        subphases = [ s for s in self.subphases if s['lote_id'] == lotId ]
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
        
        self.tableWidget.setCellWidget(idx, 3, self.createComboboxV2(idx, 3, self.getHiddenColumns(), columnSetId) )
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(dump) )

    def getRowIndex(self, ruleId):
        if not ruleId:
            return -1
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    ruleId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'colunas_ocultas_id': self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().currentIndex()
            ),
            'lote_id': self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().currentIndex()
            ),
            'subfase_id': self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().currentIndex()
            )
        }
        
    @QtCore.pyqtSlot(bool)
    def on_addBtn_clicked(self):
        self.addHiddenColumnsProfileForm = AddHiddenColumnsProfileForm(
            self.sap,
            self
        )
        self.addHiddenColumnsProfileForm.accepted.connect(self.fetchData)
        self.addHiddenColumnsProfileForm.show()

    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'colunas_ocultas_id': int(row['colunas_ocultas_id']),
                'lote_id': int(row['lote_id']),
                'subfase_id': int(row['subfase_id'])
            }
            
            for row in self.getAllTableData()
            if row['id']
        ]

    def saveTable(self):
        updateData = self.getUpdatedRows()
        if not updateData:
            return
        try:
            message = self.sap.updateHiddenColumnsProfile(updateData)
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        self.fetchData()

    def removeSelected(self):
        rowsIds = []
        while self.tableWidget.selectionModel().selectedRows():
            qModelIndex = self.tableWidget.selectionModel().selectedRows()[0]
            if self.getRowData(qModelIndex.row())['id']:
                rowsIds.append(int(self.getRowData(qModelIndex.row())['id']))
            self.tableWidget.removeRow(qModelIndex.row())
        if not rowsIds:
            return
        try:
            message = self.sap.deleteHiddenColumnsProfile(rowsIds)
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))

    @QtCore.pyqtSlot(bool)
    def on_copyBtn_clicked(self):
        if not self.getSelected():
            self.showInfo('Aviso', 'Selecione as linhas!')
            return
        self.addHiddenColumnsProfileLotForm = AddHiddenColumnsProfileLotForm(
            self.sap,
            self.getSelected(),
            self
        )
        self.addHiddenColumnsProfileLotForm.accepted.connect(self.fetchData)
        self.addHiddenColumnsProfileLotForm.show()

    def getSelected(self):
        rows = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rows.append(self.getRowData(qModelIndex.row()))
        return rows