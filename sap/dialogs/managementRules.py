# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.sap.dialogs.managementDialog  import ManagementDialog

class ManagementRules(ManagementDialog):
    
    def __init__(self, sapCtrl):
        super(ManagementRules, self).__init__(sapCtrl=sapCtrl)
        self.tableWidget.setColumnHidden(5, True)
        self.groupData = {}

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'managementRules.ui'
        )

    def getColumnsIndexToSearch(self):
        return list(range(7))

    def setGroupData(self, groupData):
        self.groupData = groupData

    def countRulesByGroup(self, groupName):
        count = 0
        for row in self.getAllTableData():
            if not (  row['grupo_regra'] == groupName ):
                continue
            count +=1
        return count

    def getGroupData(self):        
        for row in self.groupData:
            row['count'] = self.countRulesByGroup(row['grupo_regra'])
        return  self.groupData

    def connectWidgetExpression(self, row, col, ruleValue, widgetExpression):
        index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, col))
        widgetExpression.setExpression(ruleValue)
        widgetExpression.expressionChanged.connect(
            lambda *args, index=index, widget=widgetExpression: self.handleWidgetExpression(index, widget)
        )
        return widgetExpression

    def handleWidgetExpression(self, index, widget):
        self.tableWidget.setItem(index.row(), 5, self.createNotEditableItem(widget.expression()) )

    def addRow(self, 
            ruleId, 
            ruleGroup, 
            ruleSchema, 
            ruleLayer, 
            ruleField, 
            ruleValue, 
            ruleDescripition, 
            widgetExpression
        ):
        idx = self.getRowIndex(ruleId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createEditableItem(ruleId))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(ruleGroup))
        self.tableWidget.setItem(idx, 2, self.createEditableItem(ruleSchema))
        self.tableWidget.setItem(idx, 3, self.createEditableItem(ruleLayer))
        self.tableWidget.setItem(idx, 4, self.createEditableItem(ruleField))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(ruleValue))
        self.tableWidget.setItem(idx, 6, self.createEditableItem(ruleDescripition))
        self.tableWidget.setCellWidget(idx, 7, self.connectWidgetExpression(idx, 7, ruleValue, widgetExpression))

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
            'grupo_regra': self.tableWidget.model().index(rowIndex, 1).data(),
            'schema': self.tableWidget.model().index(rowIndex, 2).data(),
            'camada': self.tableWidget.model().index(rowIndex, 3).data(),
            'atributo': self.tableWidget.model().index(rowIndex, 4).data(),
            'regra': self.tableWidget.model().index(rowIndex, 5).data(),
            'descricao': self.tableWidget.model().index(rowIndex, 6).data()
        }

    def getGroupList(self):
        return [
            d['grupo_regra']
            for d in self.getGroupData()
        ]
        

    def openAddForm(self):
        self.sapCtrl.addRules(
            self.getGroupList()
        )

    def saveTable(self):
        self.sapCtrl.saveRulesSap(
            self.getAllTableData(),
            self.getGroupData()
        )

    @QtCore.pyqtSlot(bool)
    def on_editGroupBtn_clicked(self):
        self.sapCtrl.openManagementRuleSet(self.getGroupData())

    @QtCore.pyqtSlot(bool)
    def on_importCsvBtn_clicked(self):
        self.sapCtrl.importRulesCsv()