# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
from .addProjectForm import AddProjectForm
import json

class MProjects(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addProjectForm=AddProjectForm
            ):
        super(MProjects, self).__init__(controller=controller)
        self.addProjectForm = addProjectForm
        self.qgis = qgis
        self.sap = sap
        self.addProjectFormDlg = None
        self.tableWidget.setColumnHidden(6, True)
        self.showFinishedCheckBox.setChecked(False)
        self.showFinishedCheckBox.stateChanged.connect(self.fetchData)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mProjects.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getAllProjects()
        if not self.showFinishedCheckBox.isChecked():
            # Filter projects where status_id = 1
            data = [project for project in data if project.get('status_id') == 1]
        self.addRows(data)

    def addRows(self, projects):
        self.clearAllItems()
        for project in projects:
            self.addRow(
                project['id'],
                project['nome'],
                project['descricao'],
                project['nome_abrev'],
                project['status'],
                json.dumps(project)
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            name,
            description,
            alias,
            status,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setCellWidget(idx, 2, self.createLabelV2(name, idx, 2))
        self.tableWidget.setCellWidget(idx, 3, self.createLabelV2(description, idx, 3))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(alias))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(status))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(dump))
        optionColumn = 1
        self.tableWidget.setCellWidget(
            idx, 
            optionColumn, 
            self.createRowEditWidget(
                self.tableWidget,
                idx,
                optionColumn, 
                self.handleEditBtn, 
                self.handleDeleteBtn
            )
        )

    def handleEditBtn(self, index):
        data = self.getRowData(index.row())
        self.addProjectFormDlg.close() if self.addProjectFormDlg else None
        self.addProjectFormDlg = self.addProjectForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addProjectFormDlg.activeEditMode(True)
        self.addProjectFormDlg.setData(data)
        self.addProjectFormDlg.save.connect(self.fetchData)
        self.addProjectFormDlg.show()

        
    def handleDeleteBtn(self, index):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir o projeto?')
        if not result:
            return
        data = self.getRowData(index.row())
        message = self.sap.deleteProjects([data['id']])
        message and self.showInfo('Aviso', message)
        self.fetchData()

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        data = json.loads(self.tableWidget.model().index(rowIndex, 6).data())
        return {
            'id': data['id'],
            'nome': data['nome'],
            'descricao': data['descricao'],
            'nome_abrev': data['nome_abrev'],
            'status_id': data['status_id']
        }

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addProjectFormDlg.close() if self.addProjectFormDlg else None
        self.addProjectFormDlg = self.addProjectForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addProjectFormDlg.save.connect(self.fetchData)
        self.addProjectFormDlg.show()