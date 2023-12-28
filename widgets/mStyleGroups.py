# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addStyleGroupForm import AddStyleGroupForm

class MStyleGroups(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MStyleGroups, self).__init__(controller=controller)
        self.sapCtrl = sap
        self.subphases = []
        self.styles = []
        self.setWindowTitle('Grupo de Estilos')
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mStyleGroups.ui'
        )
        
    def getColumnsIndexToSearch(self):
        return [0]

    def setSubphases(self, subphases):
        self.subphases = subphases

    def setStyles(self, styles):
        self.styles = styles

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

    def addRow(self, styleId, styleName):
        idx = self.getRowIndex(styleId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(styleId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(styleName))
        self.tableWidget.setCellWidget(idx, 1, self.createOptionWidget(idx) )

    def addRows(self, styles):
        self.clearAllItems()
        for style in styles:
            self.addRow(
                style['id'],
                style['nome']
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
    
    def openAddForm(self):
        addStyleGroupForm = AddStyleGroupForm()
        if not addStyleGroupForm.exec_():
            return
        message = self.sapCtrl.createGroupStyles([addStyleGroupForm.getData()])
        self.showInfo('Aviso', message)
        self.fetchData()

    def fetchData(self):
        self.addRows(self.sapCtrl.getGroupStyles())

    def getRowData(self, rowIndex):
        return {
            'id': self.tableWidget.model().index(rowIndex, 0).data(),
            'nome': self.tableWidget.model().index(rowIndex, 2).data()
        }
    
    def handleDelete(self, row):
        try:
            message = self.sapCtrl.deleteGroupStyles([
                int(self.getRowData(row)['id'])
            ])
            self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            self.fetchData()

    def handleEdit(self, row):
        addStyleGroupForm = AddStyleGroupForm()
        currentData = self.getRowData(row)
        addStyleGroupForm.setData(currentData['nome'])
        if not addStyleGroupForm.exec_():
            return
        newData = addStyleGroupForm.getData()
        newData['id'] = int(currentData['id'])
        message = self.sapCtrl.updateGroupStyles([newData])
        self.showInfo('Aviso', message)
        self.fetchData()
        