# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addRuleProfileForm import AddRuleProfileForm
from .addRuleProfileLotForm import AddRuleProfileLotForm

class MRuleProfiles(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MRuleProfiles, self).__init__(controller=controller)
        self.sap = sap
        self.rules = []
        self.subphases = []
        self.lots = []
        self.addRuleProfileForm = None
        self.addRuleProfileLotForm = None
        self.setSubphases(self.sap.getSubphases())
        self.setRules(self.sap.getRules())
        self.setLots(self.sap.getLots())
        self.fetchData()
       
    def fetchData(self):
        self.addRows(self.sap.getRuleProfiles())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mRuleProfiles.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0]

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

    def setRules(self, rules):
        self.rules = rules

    def getRules(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.rules
        ]

    def createCombobox(self, row, col, mapValues, currentValue, handle=None ):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        combo = QtWidgets.QComboBox(self.tableWidget)
        combo.setFixedSize(QtCore.QSize(200, 30))
        if mapValues:
            for data in mapValues:
                combo.addItem(data['name'], data['value'])
            combo.setCurrentIndex(combo.findData(currentValue))
        if handle:
            index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, col))
            combo.currentIndexChanged.connect(
                lambda *args, combo=combo, index=index: handle(combo, index)
            )
        layout.addWidget(combo)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def addRow(self, profileId, layerRulesId, subphaseId, lotId):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(profileId))
        self.tableWidget.setCellWidget(idx, 1, self.createCombobox(idx, 1, self.getRules(), layerRulesId) )
        self.tableWidget.setCellWidget(idx, 2, self.createCombobox(idx, 2, self.getSubphases(), subphaseId) )
        self.tableWidget.setCellWidget(idx, 3, self.createCombobox(idx, 1, self.getLots(), lotId) )

    def addRows(self, profiles):
        self.clearAllItems()
        for profile in profiles:
            self.addRow(
                profile['id'],
                profile['layer_rules_id'],
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
        return {
            'id': self.tableWidget.model().index(rowIndex, 0).data(),
            'layer_rules_id': self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().currentIndex()
            ),
            'subfase_id': self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().currentIndex()
            ),
            'lote_id': self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().currentIndex()
            )
        }
    
    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'layer_rules_id': int(row['layer_rules_id']),
                'subfase_id': int(row['subfase_id']),
                'lote_id': int(row['lote_id'])
            }
            for row in self.getAllTableData()
            if row['id']
        ]

    def removeSelected(self):
        rowsIds = []
        while self.tableWidget.selectionModel().selectedRows():
            qModelIndex = self.tableWidget.selectionModel().selectedRows()[0]
            if self.getRowData(qModelIndex.row())['id']:
                rowsIds.append(int(self.getRowData(qModelIndex.row())['id']))
            self.tableWidget.removeRow(qModelIndex.row())
        if not rowsIds:
            return
        message = self.sap.deleteRuleProfiles(rowsIds)
        self.showInfo('Aviso', message)

    def openAddForm(self):
        self.addRuleProfileForm.close() if self.addRuleProfileForm else None
        self.addRuleProfileForm = AddRuleProfileForm(
            self.sap,
            self
        )
        self.addRuleProfileForm.accepted.connect(self.fetchData)
        self.addRuleProfileForm.show()
    
    def saveTable(self):
        updatedProfiles = self.getUpdatedRows()
        if not updatedProfiles:
            return
        message = self.sap.updateRuleProfiles(
            updatedProfiles
        )
        self.showInfo('Aviso', message)

    @QtCore.pyqtSlot(bool)
    def on_copyBtn_clicked(self):
        if not self.getSelected():
            self.showInfo('Aviso', 'Selecione as linhas!')
            return
        self.addRuleProfileLotForm.close() if self.addRuleProfileLotForm else None
        self.addRuleProfileLotForm = AddRuleProfileLotForm(
            self.sap,
            self.getSelected(),
            self
        )
        self.addRuleProfileLotForm.accepted.connect(self.fetchData)
        self.addRuleProfileLotForm.show()

    def getSelected(self):
        rows = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rows.append(self.getRowData(qModelIndex.row()))
        return rows

        