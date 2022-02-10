# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog

class MUsersPrivileges(MDialog):
    
    def __init__(self, sapCtrl):
        super(MUsersPrivileges, self).__init__(controller=sapCtrl)
        self.tableWidget.setColumnHidden(0, True)
        self.groupData = {}

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mUsersPrivileges.ui'
        )

    def getColumnsIndexToSearch(self):
        return list(range(2))

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

    def addRow(self, 
            userId, 
            userName,
            userIsAdmin,
            userIsActive
        ):
        idx = self.getRowIndex(userId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(userId))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(userName))
        self.tableWidget.setCellWidget(idx, 2, self.createCheckBox(userIsAdmin))
        self.tableWidget.setCellWidget(idx, 3, self.createCheckBox(userIsActive))

    def addRows(self, users):
        self.clearAllItems()
        for userData in users:  
            self.addRow(
                userData['uuid'], 
                userData['nome_guerra'], 
                userData['administrador'], 
                userData['ativo']
            )
        self.adjustColumns()

    def getRowIndex(self, userId):
        if not userId:
            return -1
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    userId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'uuid': self.tableWidget.model().index(rowIndex, 0).data(),
            'administrador': self.tableWidget.cellWidget(rowIndex, 2).layout().itemAt(0).widget().isChecked(),
            'ativo': self.tableWidget.cellWidget(rowIndex, 3).layout().itemAt(0).widget().isChecked()
        }

    def saveTable(self):
        self.controller.updateUsersPrivileges(
            self.getAllTableData()
        )