# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialog  import MDialog
from .addModelProfileForm import AddModelProfileForm
from .addModelProfileLotForm import AddModelProfileLotForm
from .sortComboTableWidgetItem import SortComboTableWidgetItem

class MModelProfiles(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MModelProfiles, self).__init__(controller=controller)
        self.sap = sap
        self.addModelProfileForm = None
        self.addModelProfileLotForm = None
        self.subphases = []
        self.models = []
        self.routines = []
        self.lots = []
        self.showFinishedCheckBox.setChecked(False)
        self.showFinishedCheckBox.stateChanged.connect(self.updateTable)
        self.hiddenColumns([8, 9, 10, 11])
        self.setModels(self.sap.getModels())
        self.setSubphases(self.sap.getSubphases())
        self.setRoutines(self.sap.getRoutines())
        self.updateLotsAndTable()
    
    def updateLotsAndTable(self):
        self.setLots(self.sap.getAllLots())
        self.updateTable()
    
    def updateTable(self):
        profiles = self.sap.getModelProfiles()
        if not self.showFinishedCheckBox.isChecked():
            # Criar um dicionário para mapear lote_id ao status_id
            lot_status = {lot['id']: lot['status_id'] for lot in self.lots}
            # Filtrar perfis onde o lote associado tem status_id = 1
            profiles = [profile for profile in profiles if lot_status.get(profile['lote_id']) == 1]
        self.addRows(profiles)

    def fetchData(self):
        self.updateLotsAndTable()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mModelProfiles.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0,8,9,10,11]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def setModels(self, models):
        self.models = models

    def setRoutines(self, routines):
        self.routines = routines

    def setLots(self, lots):
        # Se o checkbox não estiver marcado, filtrar apenas lotes com status_id = 1
        if not self.showFinishedCheckBox.isChecked():
            self.lots = [lot for lot in lots if lot['status_id'] == 1]
        else:
            self.lots = lots

    def getModels(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.models
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

    def getRoutines(self):
        return [
            {
                'name': d['nome'],
                'value': d['code'],
                'data': d
            }
            for d in self.routines
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

    def addRow(self, profileId, modelId, subphaseId, loteId, routineId, completion, order, parameters):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(profileId))
        
        modelCombo = self.createComboboxV2(idx, 3, self.getModels(), modelId)
        self.tableWidget.setCellWidget(idx, 3, modelCombo)
        self.tableWidget.setItem(idx, 8, self.createNotEditableItem(modelCombo.layout().itemAt(0).widget().currentText()))
        
        self.tableWidget.setCellWidget(idx, 5, self.createCheckBox(completion) )
        
        lotCombo = self.createComboboxV2(idx, 1, self.getLots(), loteId)
        self.tableWidget.setCellWidget(idx, 1, lotCombo )
        self.tableWidget.setItem(idx, 9, self.createNotEditableItem(lotCombo.layout().itemAt(0).widget().currentText()))

        routineCombo = self.createComboboxV2(idx, 4, self.getRoutines(), routineId)
        self.tableWidget.setCellWidget(idx, 4, routineCombo )
        self.tableWidget.setItem(idx, 11, self.createNotEditableItem(routineCombo.layout().itemAt(0).widget().currentText()))

        subphases = [ s for s in self.subphases if s['lote_id'] == loteId ]
        subphases.sort(key=lambda item: int(item['subfase_id']), reverse=True) 
        subphaseCombo = self.createComboboxV2(
            idx, 
            2, 
            [
                {
                    'name': d['subfase'],
                    'value': d['subfase_id'],
                    'data': d
                }
                for d in subphases
            ], 
            subphaseId
        ) 
        self.tableWidget.setCellWidget(idx, 2, subphaseCombo)
        self.tableWidget.setItem(idx, 10, self.createNotEditableItem(subphaseCombo.layout().itemAt(0).widget().currentText()))

        self.tableWidget.setItem(idx, 6, self.createEditableItem(order))
        self.tableWidget.setItem(idx, 7, self.createEditableItem(parameters))

    def addRows(self, profiles):
        self.clearAllItems()
        for modelProfile in profiles:
            self.addRow(
                modelProfile['id'],
                modelProfile['qgis_model_id'],
                modelProfile['subfase_id'],
                modelProfile['lote_id'],
                modelProfile['tipo_rotina_id'],
                modelProfile['requisito_finalizacao'],
                modelProfile['ordem'],
                modelProfile['parametros']
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
        try:
            if rowIndex < 0 or rowIndex >= self.tableWidget.rowCount():
                return {'id': None}
            id_value = self.tableWidget.model().index(rowIndex, 0).data()
            result = {'id': id_value}
            model_widget = self.tableWidget.cellWidget(rowIndex, 3)
            req_widget = self.tableWidget.cellWidget(rowIndex, 5)
            lot_widget = self.tableWidget.cellWidget(rowIndex, 1)
            routine_widget = self.tableWidget.cellWidget(rowIndex, 4)
            subphase_widget = self.tableWidget.cellWidget(rowIndex, 2)
            if model_widget and hasattr(model_widget, 'layout') and model_widget.layout() and model_widget.layout().itemAt(0):
                combo = model_widget.layout().itemAt(0).widget()
                result['qgis_model_id'] = combo.itemData(combo.currentIndex())
            else:
                result['qgis_model_id'] = None
            if req_widget and hasattr(req_widget, 'layout') and req_widget.layout() and req_widget.layout().itemAt(0):
                result['requisito_finalizacao'] = req_widget.layout().itemAt(0).widget().isChecked()
            else:
                result['requisito_finalizacao'] = False
            if lot_widget and hasattr(lot_widget, 'layout') and lot_widget.layout() and lot_widget.layout().itemAt(0):
                combo = lot_widget.layout().itemAt(0).widget()
                result['lote_id'] = combo.itemData(combo.currentIndex())
            else:
                result['lote_id'] = None
            if routine_widget and hasattr(routine_widget, 'layout') and routine_widget.layout() and routine_widget.layout().itemAt(0):
                combo = routine_widget.layout().itemAt(0).widget()
                result['tipo_rotina_id'] = combo.itemData(combo.currentIndex())
            else:
                result['tipo_rotina_id'] = None
            if subphase_widget and hasattr(subphase_widget, 'layout') and subphase_widget.layout() and subphase_widget.layout().itemAt(0):
                combo = subphase_widget.layout().itemAt(0).widget()
                result['subfase_id'] = combo.itemData(combo.currentIndex())
            else:
                result['subfase_id'] = None
            ordem_index = self.tableWidget.model().index(rowIndex, 6)
            if ordem_index.isValid():
                result['ordem'] = int(ordem_index.data() or 0)
            else:
                result['ordem'] = 0
            parametros_index = self.tableWidget.model().index(rowIndex, 7)
            if parametros_index.isValid():
                result['parametros'] = parametros_index.data() or ''
            else:
                result['parametros'] = ''
            return result
        except Exception as e:
            return {'id': None}

    def getUpdatedRows(self):
        return [
             {
                'id': int(row['id']),
                'qgis_model_id': row['qgis_model_id'],
                'requisito_finalizacao': row['requisito_finalizacao'],
                'subfase_id': row['subfase_id'],
                'tipo_rotina_id': row['tipo_rotina_id'],
                'lote_id': row['lote_id'],
                'ordem': int(row['ordem']),
                'parametros': row['parametros']
            }
            for row in self.getAllTableData()
            if row['id']
        ]

    def removeSelected(self):
        rowsIds = []
        selectedRows = sorted(set([index.row() for index in self.tableWidget.selectionModel().selectedRows()]), reverse=True)
        for rowIndex in selectedRows:
            try:
                rowData = self.getRowData(rowIndex)
                if rowData and rowData.get('id'):
                    rowsIds.append(int(rowData['id']))
                self.tableWidget.removeRow(rowIndex)
            except Exception as e:
                print(f"Error removing row {rowIndex}: {str(e)}")
        if not rowsIds:
            return
        try:
            message = self.sap.deleteModelProfiles(rowsIds)
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Erro', f"Falha ao excluir perfis: {str(e)}")

    def openAddForm(self):
        self.addModelProfileForm.close() if self.addModelProfileForm else None
        self.addModelProfileForm = AddModelProfileForm(
            self.sap,
            self
        )
        self.addModelProfileForm.accepted.connect(self.fetchData)
        self.addModelProfileForm.show()
    
    def saveTable(self):
        updatedFmeProfiles = self.getUpdatedRows()
        if not updatedFmeProfiles:
            return
        message = self.sap.updateModelProfiles(updatedFmeProfiles)
        message and self.showInfo('Aviso', message)

    @QtCore.pyqtSlot(bool)
    def on_copyBtn_clicked(self):
        if not self.getSelected():
            self.showInfo('Aviso', 'Selecione as linhas!')
            return
        self.addModelProfileLotForm.close() if self.addModelProfileLotForm else None
        self.addModelProfileLotForm = AddModelProfileLotForm(
            self.sap,
            self.getSelected(),
            self
        )
        self.addModelProfileLotForm.accepted.connect(self.fetchData)
        self.addModelProfileLotForm.show()

    def getSelected(self):
        rows = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rows.append(self.getRowData(qModelIndex.row()))
        return rows