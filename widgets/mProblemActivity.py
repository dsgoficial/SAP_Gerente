# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2
from .addShortcutForm import AddShortcutForm
import json
from qgis.core import QgsGeometry
from Ferramentas_Gerencia.modules.qgis.mapFunctions.createTemporaryLayer  import CreateTemporaryLayer
from Ferramentas_Gerencia.modules.qgis.factories.qgisApiSingleton import QgisApiSingleton

class MProblemActivity(MDialogV2):
    
    def __init__(self, controller, qgis, sap):
        super(MProblemActivity, self).__init__(controller=controller)
        self.sap = sap
        self.qgis = qgis
        self.addForm = None
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(9, True)
        self.fetchTableData()

    def fetchTableData(self):
        self.addRows(self.sap.getProblemActivity())

    def getColumnsIndexToSearch(self):
        return [0,2,3,4]

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mProblemActivity.ui'
        )

    def addRows(self, models):
        self.clearAllItems()
        for data in models:
            self.addRow(
                data['id'],
                data['atividade_id'],
                data['usuario'],
                data['tipo_problema'],
                data['descricao'],
                data['data'],
                data['resolvido'],
                data['geom'],
                json.dumps(data)
            )
        self.adjustColumns()

    def addRow(
            self, 
            primaryKey, 
            acitivyId, 
            user, 
            problemType, 
            description,
            date,
            fixed,
            ewkt,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(acitivyId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(user))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(problemType))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(description))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(date))
        
        self.tableWidget.setCellWidget(
            idx, 
            6, 
            self.createCheckbox(        
                fixed,
                lambda state, problemId=primaryKey: self.setFixedProblem(state, problemId)
            )
        )
        
        self.tableWidget.setCellWidget(
            idx, 
            7, 
            self.createButton(        
                'Abrir',
                lambda b, acitivyId=acitivyId: self.openActivity(acitivyId)
            )
        )
        
        self.tableWidget.setCellWidget(
            idx, 
            8, 
            self.createButton(        
                'Carregar',
                lambda b, ewkt=ewkt: self.loadProblemLocate(ewkt)
            )
        )
        
        self.tableWidget.setItem(idx, 9, self.createNotEditableItem(dump))

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def createCheckbox(self, checked, handle ):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        ckb = QtWidgets.QCheckBox()
        ckb.setChecked(checked)
        ckb.stateChanged.connect(handle)
        layout.addWidget(ckb)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def createButton(self, name, handle):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        btn = QtWidgets.QPushButton(name)
        btn.clicked.connect(handle)
        layout.addWidget(btn)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def setFixedProblem(self, state, problemId):
        message = self.sap.updateProblemActivity([{
            'id': problemId,
            'resolvido': state == QtCore.Qt.Checked
        }])
        self.showInfo('Aviso', message)
        self.fetchTableData()

    def openActivity(self, activityId):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.qgis.startSapFP(
            self.sap.getActivityDataById(activityId)
        )
        QtWidgets.QApplication.restoreOverrideCursor()

    def loadProblemLocate(self, ewkt):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        temporaryLayer = CreateTemporaryLayer().run(
            'local_de_erro', 
            'polygon', 
            ['id'], 
            "EPSG:{}".format(ewkt.split(';')[0].split('=')[1])
        )
        qgisApi = QgisApiSingleton.getInstance()
        qgisApi.addFeature(
            temporaryLayer, 
            {
                'id': 0
            }, 
            QgsGeometry().fromWkt(ewkt.split(';')[1])
        )
        qgisApi.addLayerOnMap(temporaryLayer)
        QtWidgets.QApplication.restoreOverrideCursor()

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'ferramenta': self.tableWidget.model().index(rowIndex, 2).data(),
            'idioma': self.tableWidget.model().index(rowIndex, 3).data(),   
            'atalho': self.tableWidget.model().index(rowIndex, 4).data()
        }

        