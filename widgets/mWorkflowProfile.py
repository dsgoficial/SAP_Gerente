# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2
from .addWorkflowProfileForm import AddWorkflowProfileForm
from .addWorkflowProfileLotForm import AddWorkflowProfileLotForm
from .sortComboTableWidgetItem import SortComboTableWidgetItem

class MWorkflowProfile(MDialogV2):
    
    def __init__(self, controller, qgis, sap):
        super(MWorkflowProfile, self).__init__(controller=controller)
        self.sap = sap
        self.addWorkflowProfileForm = None
        self.addWorkflowProfileLotForm = None
        self.setSubphases(self.sap.getSubphases())
        self.setWorkflows(self.sap.getWorkflows())
        self.setLots(self.sap.getLots())
        self.fetchData()
    
    def fetchData(self):
        self.addRows(self.sap.getWorkflowProfiles())

    def addRows(self, data):
        self.clearAllItems()
        for d in data:
            self.addRow(
                d['id'],
                d['workflow_dsgtools_id'],
                d['subfase_id'],
                d['lote_id'],
                d['requisito_finalizacao']
            )
        self.adjustColumns()

    def addRow(self, profileId, workflowId, subphaseId, loteId, completion):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(profileId))
        lotCombo = self.createComboboxV2(idx, 1, self.getLots(), loteId)
        self.tableWidget.setCellWidget(idx, 1, lotCombo )
        subphases = [ s for s in self.getSubphases() if s['data']['lote_id'] == loteId ]
        subphases.sort(key=lambda item: int(item['value']), reverse=True) 
        subphaseCombo = self.createComboboxV2(
            idx, 
            2, 
            subphases, 
            subphaseId
        ) 
        self.tableWidget.setCellWidget(idx, 2, subphaseCombo)
        workflowCombo = self.createComboboxV2(idx, 3, self.getWorkflows(), workflowId)
        self.tableWidget.setCellWidget(idx, 3, workflowCombo)
        self.tableWidget.setCellWidget(idx, 4, self.createCheckBox(completion) )

    def getRowIndex(self, profileId):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    profileId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mWorkflowProfiles.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0,8,9,10,11]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def setWorkflows(self, workflows):
        self.workflows = workflows

    def setLots(self, lots):
        self.lots = lots

    def getWorkflows(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.workflows
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

    def getSubphases(self):
        return [
            {
                'name': d['subfase'],
                'value': d['subfase_id'],
                'data': d
            }
            for d in self.subphases
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

    def getRowData(self, rowIndex):
        return {
            'id': self.tableWidget.model().index(rowIndex, 0).data(),
            'requisito_finalizacao': self.tableWidget.cellWidget(rowIndex, 4).layout().itemAt(0).widget().isChecked(),
            'lote_id': self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().currentIndex()
            ),
            'subfase_id': self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().currentIndex()
            ),
            'workflow_dsgtools_id': self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().currentIndex()
            )
        }

    def getUpdatedRows(self):
        return [
             {
                'id': int(row['id']),
                'requisito_finalizacao': row['requisito_finalizacao'],
                'subfase_id': row['subfase_id'],
                'lote_id': row['lote_id'],
                'workflow_dsgtools_id': row['workflow_dsgtools_id']
            }
            for row in self.getAllTableData()
            if row['id']
        ]

    @QtCore.pyqtSlot(bool)
    def on_delBtn_clicked(self):
        rowsIds = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rowsIds.append(int(self.getRowData(qModelIndex.row())['id']))
        try:
            message = self.sap.deleteWorkflowProfiles(rowsIds)
            self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
            return ''  
        self.fetchData()

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addWorkflowProfileForm.close() if self.addWorkflowProfileForm else None
        self.addWorkflowProfileForm = AddWorkflowProfileForm(
            self.sap,
            self
        )
        self.addWorkflowProfileForm.accepted.connect(self.fetchData)
        self.addWorkflowProfileForm.show()
    
    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        updatedProfiles = self.getUpdatedRows()
        if not updatedProfiles:
            return
        message = self.sap.updateWorkflowProfiles(updatedProfiles)
        self.showInfo('Aviso', message)

    @QtCore.pyqtSlot(bool)
    def on_copyBtn_clicked(self):
        if not self.getSelected():
            self.showInfo('Aviso', 'Selecione as linhas!')
            return
        self.addWorkflowProfileLotForm.close() if self.addWorkflowProfileLotForm else None
        self.addWorkflowProfileLotForm = AddWorkflowProfileLotForm(
            self.sap,
            self.getSelected(),
            self
        )
        self.addWorkflowProfileLotForm.accepted.connect(self.fetchData)
        self.addWorkflowProfileLotForm.show()

    def getSelected(self):
        rows = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rows.append(self.getRowData(qModelIndex.row()))
        return rows
        