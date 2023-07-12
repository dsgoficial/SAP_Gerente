# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addThemeForm import AddThemeForm
import json

class MThemes(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MThemes, self).__init__(controller=controller)
        self.groupData = {}
        self.sap = sap
        self.addThemeForm = None
        self.hiddenColumns([3,4])
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mThemes.ui'
        )

    def getColumnsIndexToSearch(self):
        return [0,1]

    def addRow(self, 
            primaryKey, 
            name, 
            value,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(name))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(value))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(dump))
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
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir?')
        if not result:
            return
        try:
            message = self.sap.deleteThemes([
                int(self.getRowData(row)['id'])
            ])
            self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            self.fetchData()

    def fetchData(self):
        self.addRows(self.sap.getThemes())

    def handleEdit(self, row):   
        currentData = self.getRowData(row)
        self.addThemeForm = AddThemeForm(self.sap, self)
        self.addThemeForm.setData(
            currentData['id'],
            currentData['nome'],
            currentData['definicao_tema']
        )
        self.addThemeForm.activeEditMode(True)
        self.addThemeForm.accepted.connect(self.fetchData)
        self.addThemeForm.show()
        

    def handleDownloadBtn(self, row):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                   'Salvar Arquivo',
                                                   "tema",
                                                  '*.json')
        if not filePath[0]:
            return
        with open(filePath[0], 'w') as f:
            f.write( self.tableWidget.model().index( row, 3 ).data() )
        self.showInfo('Aviso', "Salvo com sucesso!")

    def addRows(self, data):
        self.clearAllItems()
        for d in data:  
            self.addRow(
                str(d['id']), 
                d['nome'], 
                d['definicao_tema'],
                json.dumps(d)
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
        return json.loads(self.tableWidget.model().index(rowIndex, 4).data())
        
    @QtCore.pyqtSlot(bool)
    def on_addBtn_clicked(self):
        self.addThemeForm = AddThemeForm(self.sap, self)
        self.addThemeForm.accepted.connect(self.fetchData)
        self.addThemeForm.show()