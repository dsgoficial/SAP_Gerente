# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog
from .addRuleFormV2 import AddRuleFormV2

class MRules(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MRules, self).__init__(controller=controller)
        self.tableWidget.setColumnHidden(3, True)
        self.groupData = {}
        self.sap = sap
        self.addRuleFormV2 = None
        self.addRows(self.sap.getRules())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mRules.ui'
        )

    def getColumnsIndexToSearch(self):
        return [0,1]

    def addRow(self, 
            ruleId, 
            ruleName, 
            ruleValue
        ):
        idx = self.getRowIndex(ruleId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(ruleId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(ruleName))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(ruleValue))
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
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir regra?')
        if not result:
            return
        try:
            message = self.sap.deleteRules([
                int(self.getRowData(row)['id'])
            ])
            self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            self.fetchData()

    def fetchData(self):
        self.addRows(self.sap.getRules())

    def handleEdit(self, row):   
        currentData = self.getRowData(row)
        self.addRuleFormV2.close() if self.addRuleFormV2 else None
        self.addRuleFormV2 = AddRuleFormV2(
            self.sap,
            self
        )
        self.addRuleFormV2.setData(
            currentData['id'],
            currentData['nome'],
            currentData['regra']
        )
        self.addRuleFormV2.accepted.connect(self.fetchData)
        self.addRuleFormV2.show()

    def handleDownloadBtn(self, row):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                   'Salvar Arquivo',
                                                   "regra",
                                                  '*.json')
        if not filePath[0]:
            return
        with open(filePath[0], 'w') as f:
            f.write( self.tableWidget.model().index( row, 3 ).data() )
        self.showInfo('Aviso', "Regra salva com sucesso!")

    def addRows(self, rules):
        self.clearAllItems()
        for ruleData in rules:  
            self.addRow(
                str(ruleData['id']), 
                ruleData['nome'], 
                ruleData['regra']
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
            'nome': self.tableWidget.model().index(rowIndex, 2).data(),
            'regra': self.tableWidget.model().index(rowIndex, 3).data()
        }
        
    @QtCore.pyqtSlot(bool)
    def on_addBtn_clicked(self):
        self.addRuleFormV2.close() if self.addRuleFormV2 else None
        self.addRuleFormV2 = AddRuleFormV2(
            self.sap,
            self
        )
        self.addRuleFormV2.accepted.connect(self.fetchData)
        self.addRuleFormV2.show()