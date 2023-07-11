# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addThemesProfileForm import AddThemesProfileForm
from .addThemesProfileLotForm import AddThemesProfileLotForm
from .sortComboTableWidgetItem import SortComboTableWidgetItem
import json

class MThemesProfile(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MThemesProfile, self).__init__(controller=controller)
        self.tableWidget.setColumnHidden(4, True)
        self.groupData = {}
        self.sap = sap
        self.lots = []
        self.subphases = []
        self.themes = []
        self.addThemesProfileForm = None
        self.addThemesProfileLotForm = None
        self.setSubphases(self.sap.getSubphases())
        self.setThemes(self.sap.getThemes())
        self.setLots(self.sap.getLots())
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mThemesProfile.ui'
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

    def setThemes(self, themes):
        self.themes = themes

    def getThemes(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.themes
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

    def createOptionWidget(self, row):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        for button in self.getRowOptionSetup(row):
            btn = self.createTableToolButton(button['tooltip'], button['iconPath'] )
            btn.clicked.connect(button['callback'])
            layout.addWidget(btn)
        layout.setAlignment(QtCore.Qt.AlignCenter)
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
            message = self.sap.deleteThemesProfile([
                int(self.getRowData(row)['id'])
            ])
            self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            self.fetchData()

    def fetchData(self):
        self.addRows(self.sap.getThemesProfile())

    def addRows(self, data):
        self.clearAllItems()
        for d in data:  
            self.addRow(
                str(d['id']), 
                d['tema'], 
                d['subfase_id'], 
                d['lote_id'], 
                d['tema_id'],
                json.dumps(d)
            )
        self.adjustColumns()

    def addRow(self, 
            relId, 
            theme,
            subphaseId,
            lotId,
            themId, 
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
        
        self.tableWidget.setCellWidget(idx, 3, self.createComboboxV2(idx, 3, self.getThemes(), themId) )
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
            'tema_id': self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().itemData(
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
        self.addThemesProfileForm = AddThemesProfileForm(
            self.sap,
            self
        )
        self.addThemesProfileForm.accepted.connect(self.fetchData)
        self.addThemesProfileForm.show()

    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'tema_id': int(row['tema_id']),
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
            message = self.sap.updateThemesProfile(updateData)
            self.showInfo('Aviso', message)
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
            message = self.sap.deleteThemesProfile(rowsIds)
            self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))

    @QtCore.pyqtSlot(bool)
    def on_copyBtn_clicked(self):
        if not self.getSelected():
            self.showInfo('Aviso', 'Selecione as linhas!')
            return
        self.addThemesProfileLotForm = AddThemesProfileLotForm(
            self.sap,
            self.getSelected(),
            self
        )
        self.addThemesProfileLotForm.accepted.connect(self.fetchData)
        self.addThemesProfileLotForm.show()

    def getSelected(self):
        rows = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rows.append(self.getRowData(qModelIndex.row()))
        return rows