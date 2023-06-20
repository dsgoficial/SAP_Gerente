# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addInpuGroupForm import AddInpuGroupForm

class MInputGroup(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MInputGroup, self).__init__(controller=controller)
        self.tableWidget.setColumnHidden(3, True)
        self.groupData = {}
        self.sap = sap
        self.addInpuGroupForm = None
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mInputGroup.ui'
        )

    def getColumnsIndexToSearch(self):
        return [0,2]

    def fetchData(self):
        self.addRows(self.sap.getInputGroups())

    def addRows(self, menus):
        self.clearAllItems()
        for menu in menus:  
            self.addRow(
                str(menu['id']), 
                menu['nome']
            )
        self.adjustColumns()

    def addRow(self, 
            menuId, 
            menuName
        ):
        idx = self.getRowIndex(menuId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(menuId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(menuName))
        self.tableWidget.setCellWidget(idx, 1, self.createOptionWidget(idx) )

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

    def handleEdit(self, row):   
        currentData = self.getRowData(row)
        self.addInpuGroupForm = AddInpuGroupForm(self.sap, self)
        self.addInpuGroupForm.setData(
            currentData['id'],
            currentData['nome']
        )
        self.addInpuGroupForm.accepted.connect(self.fetchData)
        self.addInpuGroupForm.show()
        
    def handleDelete(self, row):
        try:
            message = self.sap.deleteInputGroups([
                int(self.getRowData(row)['id'])
            ])
            self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            self.fetchData()

    def getRowIndex(self, menuId):
        if not menuId:
            return -1
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    menuId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'nome': self.tableWidget.model().index(rowIndex, 2).data()
        }
        
    @QtCore.pyqtSlot(bool)
    def on_addBtn_clicked(self):
        self.addInpuGroupForm = AddInpuGroupForm(self.sap, self)
        self.addInpuGroupForm.accepted.connect(self.fetchData)
        self.addInpuGroupForm.show()