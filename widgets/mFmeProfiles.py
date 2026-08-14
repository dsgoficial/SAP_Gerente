# -*- coding: utf-8 -*-
import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialog  import MDialog
from .addFmeProfileForm import AddFmeProfileForm
from .sortComboTableWidgetItem import SortComboTableWidgetItem

class MFmeProfiles(MDialog):

    # Ordem das colunas de mFmeProfiles.ui. Espelha a tela de perfil de modelo.
    COL_ID = 0
    COL_LOTE = 1
    COL_SUBFASE = 2
    COL_SERVIDOR = 3
    COL_ROTINA = 4
    COL_TIPO_ROTINA = 5
    COL_FINALIZACAO = 6
    COL_ORDEM = 7

    def __init__(self, controller, qgis, sap, fme):
        super(MFmeProfiles, self).__init__(controller=controller)
        self.sap = sap
        self.fme = fme
        self.subphases = []
        self.fmeServers = []
        self.fmeRoutines = []
        self.routineTypes = []
        self.lots = []
        self.setFmeServers(self.sap.getFmeServers())
        self.setSubphases(self.sap.getSubphases())
        self.setRoutineTypes(self.sap.getRoutines())
        self.setLots(self.sap.getAllLots())
        self.fetchData()

    def fetchData(self):
        self.addRows(self.sap.getFmeProfiles())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mFmeProfiles.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def getSubphasesByLotId(self, lotId):
        """A rota projeto/subfases devolve `subfase_id`, `subfase`, `fase` e
        `lote_id`. A mesma subfase aparece uma vez por lote, logo o filtro por
        lote e obrigatorio: subfase_id sozinho nao determina o lote."""
        subphases = [ s for s in self.subphases if s['lote_id'] == lotId ]
        subphases.sort(key=lambda item: int(item['subfase_id']), reverse=True)
        return [
            {
                'name': "{} - {}".format(d['fase'], d['subfase']),
                'value': d['subfase_id'],
                'data': d
            }
            for d in subphases
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

    def setRoutineTypes(self, routineTypes):
        self.routineTypes = routineTypes

    def getRoutineTypes(self):
        return [
            {
                'name': d['nome'],
                'value': d['code'],
                'data': d
            }
            for d in self.routineTypes
        ]

    def setFmeServers(self, fmeServers):
        self.fmeServers = fmeServers

    def getFmeServers(self):
        # projeto/configuracao/gerenciador_fme devolve {id, url}
        return [
            {
                'name': d['url'],
                'value': d['id'],
                'data': d
            }
            for d in self.fmeServers
        ]

    def getFmeRoutinesByServerId(self, profileFmeServerId):
        for server in self.getFmeServers():
            if server['data']['id'] == profileFmeServerId:
                return [
                    {
                        'name': routine['rotina'],
                        'value': routine['id']
                    }
                    for routine in self.controller.getFmeRoutines(server['data']['url'])
                ]
        return []

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
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def handleServerCombo(self, combo, index):
        serverId = combo.itemData(combo.currentIndex())
        routines = self.getFmeRoutinesByServerId(serverId)
        routines.append({
            'name': '...',
            'value': None
        })
        self.tableWidget.setCellWidget(
            index.row(),
            self.COL_ROTINA,
            self.createCombobox(index.row(), self.COL_ROTINA, routines, None)
        )

    def handleLotCombo(self, combo, index):
        """Trocar o lote troca o conjunto de subfases da linha."""
        lotId = combo.itemData(combo.currentIndex())
        self.tableWidget.setCellWidget(
            index.row(),
            self.COL_SUBFASE,
            self.createCombobox(index.row(), self.COL_SUBFASE, self.getSubphasesByLotId(lotId), None)
        )

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

    def addRow(self, profileId, profileFmeServerId, fmeRoutineId, subphase, lotId, routineTypeId, completion, order):
        idx = self.getRowIndex(profileId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, self.COL_ID, self.createNotEditableItemNumber(profileId))

        self.tableWidget.setItem(idx, self.COL_LOTE, SortComboTableWidgetItem())
        self.tableWidget.setCellWidget(idx, self.COL_LOTE, self.createCombobox(idx, self.COL_LOTE, self.getLots(), lotId, self.handleLotCombo))

        self.tableWidget.setItem(idx, self.COL_SUBFASE, SortComboTableWidgetItem())
        self.tableWidget.setCellWidget(idx, self.COL_SUBFASE, self.createCombobox(idx, self.COL_SUBFASE, self.getSubphasesByLotId(lotId), subphase))

        self.tableWidget.setItem(idx, self.COL_SERVIDOR, SortComboTableWidgetItem())
        self.tableWidget.setCellWidget(idx, self.COL_SERVIDOR, self.createCombobox(idx, self.COL_SERVIDOR, self.getFmeServers(), profileFmeServerId, self.handleServerCombo))

        self.tableWidget.setItem(idx, self.COL_ROTINA, SortComboTableWidgetItem())
        self.tableWidget.setCellWidget(idx, self.COL_ROTINA, self.createCombobox(idx, self.COL_ROTINA, self.getFmeRoutinesByServerId(profileFmeServerId), fmeRoutineId))

        self.tableWidget.setItem(idx, self.COL_TIPO_ROTINA, SortComboTableWidgetItem())
        self.tableWidget.setCellWidget(idx, self.COL_TIPO_ROTINA, self.createCombobox(idx, self.COL_TIPO_ROTINA, self.getRoutineTypes(), routineTypeId))

        self.tableWidget.setCellWidget(idx, self.COL_FINALIZACAO, self.createCheckBox(completion))

        self.tableWidget.setItem(idx, self.COL_ORDEM, self.createEditableItem(order))

    def addRows(self, profiles):
        self.clearAllItems()
        for fmeProfile in profiles:
            self.addRow(
                fmeProfile['id'],
                fmeProfile['gerenciador_fme_id'],
                fmeProfile['rotina'],
                fmeProfile['subfase_id'],
                fmeProfile['lote_id'],
                fmeProfile['tipo_rotina_id'],
                fmeProfile['requisito_finalizacao'],
                fmeProfile['ordem']
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

    def getComboData(self, rowIndex, column):
        widget = self.tableWidget.cellWidget(rowIndex, column)
        if not (widget and widget.layout() and widget.layout().itemAt(0)):
            return None
        combo = widget.layout().itemAt(0).widget()
        return combo.itemData(combo.currentIndex())

    def getRowData(self, rowIndex):
        finalizacao = self.tableWidget.cellWidget(rowIndex, self.COL_FINALIZACAO)
        return {
            'id': self.tableWidget.model().index(rowIndex, self.COL_ID).data(),
            'lote_id': self.getComboData(rowIndex, self.COL_LOTE),
            'subfase_id': self.getComboData(rowIndex, self.COL_SUBFASE),
            'gerenciador_fme_id': self.getComboData(rowIndex, self.COL_SERVIDOR),
            'rotina': self.getComboData(rowIndex, self.COL_ROTINA),
            'tipo_rotina_id': self.getComboData(rowIndex, self.COL_TIPO_ROTINA),
            'requisito_finalizacao': finalizacao.layout().itemAt(0).widget().isChecked() if finalizacao else False,
            'ordem': int(self.tableWidget.model().index(rowIndex, self.COL_ORDEM).data() or 0)
        }

    def getAddedRows(self):
        # As chaves batem com projeto_schema.js models.perfisFME
        return [
            {
                'gerenciador_fme_id': row['gerenciador_fme_id'],
                'rotina': row['rotina'],
                'requisito_finalizacao': row['requisito_finalizacao'],
                'tipo_rotina_id': row['tipo_rotina_id'],
                'subfase_id': row['subfase_id'],
                'lote_id': row['lote_id'],
                'ordem': int(row['ordem'])
            }
            for row in self.getAllTableData()
            if not row['id']
        ]

    def getUpdatedRows(self):
        # As chaves batem com projeto_schema.js models.perfilFMEAtualizacao
        return [
            {
                'id': int(row['id']),
                'gerenciador_fme_id': row['gerenciador_fme_id'],
                'rotina': row['rotina'],
                'requisito_finalizacao': row['requisito_finalizacao'],
                'tipo_rotina_id': row['tipo_rotina_id'],
                'subfase_id': row['subfase_id'],
                'lote_id': row['lote_id'],
                'ordem': int(row['ordem'])
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
        if not rowsIds:
            return
        message = self.sap.deleteFmeProfiles(rowsIds)
        message and self.showInfo('Aviso', message)

    def openAddForm(self):
        self.addFmeProfileForm = AddFmeProfileForm(
            self.sap, 
            self.fme,
            self
        )
        self.addFmeProfileForm.show()
    
    def saveTable(self):
        updatedFmeProfiles = self.getUpdatedRows()
        if not updatedFmeProfiles:
            return
        message = self.sap.updateFmeProfiles(
            updatedFmeProfiles
        )
        message and self.showInfo('Aviso', message)
      
        