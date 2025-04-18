# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialog  import MDialog
from .addMenuProfileForm import AddMenuProfileForm
from .addMenuProfileLotForm import AddMenuProfileLotForm
from .sortComboTableWidgetItem import SortComboTableWidgetItem

class MMenuProfile(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MMenuProfile, self).__init__(controller=controller)
        self.tableWidget.setColumnHidden(5, True)
        self.groupData = {}
        self.sap = sap
        self.lots = []
        self.subphases = []
        self.menus = []
        self.addMenuProfileForm = None
        self.addMenuProfileLotForm = None
        self.showFinishedCheckBox.setChecked(False)
        self.showFinishedCheckBox.stateChanged.connect(self.updateTable)
        self.setSubphases(self.sap.getSubphases())
        self.setMenus(self.sap.getMenus())
        self.updateLotsAndTable()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mMenuProfiles.ui'
        )

    def getColumnsIndexToSearch(self):
        return [0,1]
    
    def updateLotsAndTable(self):
        self.setLots(self.sap.getAllLots())
        self.updateTable()

    def updateTable(self):
        profiles = self.sap.getMenuProfiles()
        if not self.showFinishedCheckBox.isChecked():
            # Criar um dicionário para mapear lote_id ao status_id
            lot_status = {lot['id']: lot['status_id'] for lot in self.lots}
            # Filtrar perfis onde o lote associado tem status_id = 1
            profiles = [profile for profile in profiles if lot_status.get(profile['lote_id']) == 1]
        self.addRows(profiles)

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
        # Se o checkbox não estiver marcado, filtrar apenas lotes com status_id = 1
        if not self.showFinishedCheckBox.isChecked():
            self.lots = [lot for lot in lots if lot['status_id'] == 1]
        else:
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

    def setMenus(self, menus):
        self.menus = menus

    def getMenus(self):
        return [
            {
                'name': d['nome'],
                'value': d['id'],
                'data': d
            }
            for d in self.menus
        ]

    def addRow(self, 
            relId, 
            menuName,
            subphaseId,
            lotId,
            rev, 
            menuId
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
        
        self.tableWidget.setCellWidget(idx, 3, self.createComboboxV2(idx, 3, self.getMenus(), menuId) )
        self.tableWidget.setCellWidget(idx, 4, self.createCheckBox(rev)  )
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(menuId) )

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
            message = self.sap.deleteMenuProfiles([
                int(self.getRowData(row)['id'])
            ])
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            self.fetchData()

    def fetchData(self):
        self.updateLotsAndTable()

    def addRows(self, rules):
        self.clearAllItems()
        for ruleData in rules:  
            self.addRow(
                str(ruleData['id']), 
                ruleData['nome'], 
                ruleData['subfase_id'], 
                ruleData['lote_id'], 
                ruleData['menu_revisao'], 
                ruleData['menu_id']
            )
        self.adjustColumns()

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
            'menu_id': self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().currentIndex()
            ),
            'lote_id': self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 1).layout().itemAt(0).widget().currentIndex()
            ),
            'subfase_id': self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().itemData(
                self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().currentIndex()
            ),
            'menu_revisao': self.tableWidget.cellWidget(rowIndex, 4).layout().itemAt(0).widget().isChecked()
        }
        
    @QtCore.pyqtSlot(bool)
    def on_addBtn_clicked(self):
        self.addMenuProfileForm = AddMenuProfileForm(
            self.sap,
            self
        )
        self.addMenuProfileForm.accepted.connect(self.fetchData)
        self.addMenuProfileForm.show()

    def getUpdatedRows(self):
        return [
            {
                'id': int(row['id']),
                'menu_id': int(row['menu_id']),
                'lote_id': int(row['lote_id']),
                'subfase_id': int(row['subfase_id']),
                'menu_revisao': row['menu_revisao']
            }
            
            for row in self.getAllTableData()
            if row['id']
        ]

    def saveTable(self):
        updateData = self.getUpdatedRows()
        if not updateData:
            return
        try:
            message = self.sap.updateMenuProfiles(updateData)
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
            message = self.sap.deleteMenuProfiles(rowsIds)
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))

    @QtCore.pyqtSlot(bool)
    def on_copyBtn_clicked(self):
        if not self.getSelected():
            self.showInfo('Aviso', 'Selecione as linhas!')
            return
        self.addMenuProfileLotForm = AddMenuProfileLotForm(
            self.sap,
            self.getSelected(),
            self
        )
        self.addMenuProfileLotForm.accepted.connect(self.fetchData)
        self.addMenuProfileLotForm.show()

    def getSelected(self):
        rows = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rows.append(self.getRowData(qModelIndex.row()))
        return rows