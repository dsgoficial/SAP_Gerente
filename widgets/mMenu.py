# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addMenuForm import AddMenuForm

class MMenu(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MMenu, self).__init__(controller=controller)
        self.tableWidget.setColumnHidden(3, True)
        self.groupData = {}
        self.sap = sap
        self.addMenuForm = None
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mMenu.ui'
        )

    def getColumnsIndexToSearch(self):
        return [0,1]

    def addRow(self, 
            menuId, 
            menuName, 
            menuValue
        ):
        idx = self.getRowIndex(menuId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(menuId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(menuName))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(menuValue))
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
            },
            {
                'tooltip': 'Download',
                'iconPath': self.getDownloadIconPath(),
                'callback': lambda b, row=row: self.handleDownloadBtn(row) 
            }
        ]

    def handleDelete(self, row):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir menu?')
        if not result:
            return
        try:
            message = self.sap.deleteMenus([
                int(self.getRowData(row)['id'])
            ])
            self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            self.fetchData()

    def fetchData(self):
        self.addRows(self.sap.getMenus())

    def handleEdit(self, row):   
        currentData = self.getRowData(row)
        self.addMenuForm = AddMenuForm(self.sap, self)
        self.addMenuForm.setData(
            currentData['id'],
            currentData['nome'],
            currentData['definicao_menu']
        )
        self.addMenuForm.activeEditMode(True)
        self.addMenuForm.accepted.connect(self.fetchData)
        self.addMenuForm.show()
        

    def handleDownloadBtn(self, row):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                   'Salvar Arquivo',
                                                   "menu",
                                                  '*.json')
        if not filePath[0]:
            return
        with open(filePath[0], 'w') as f:
            f.write( self.tableWidget.model().index( row, 3 ).data() )
        self.showInfo('Aviso', "Menu salvo com sucesso!")

    def addRows(self, menus):
        self.clearAllItems()
        for menu in menus:  
            self.addRow(
                str(menu['id']), 
                menu['nome'], 
                menu['definicao_menu']
            )
        self.adjustColumns()

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
            'nome': self.tableWidget.model().index(rowIndex, 2).data(),
            'definicao_menu': self.tableWidget.model().index(rowIndex, 3).data()
        }
        
    @QtCore.pyqtSlot(bool)
    def on_addBtn_clicked(self):
        self.addMenuForm = AddMenuForm(self.sap, self)
        self.addMenuForm.accepted.connect(self.fetchData)
        self.addMenuForm.show()