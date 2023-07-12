# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog

class MLastCompletedActivities(MDialog):
    
    def __init__(self, controller, qgis, sap):
        super(MLastCompletedActivities, self).__init__(controller=controller)
        self.sap = sap
        self.hiddenColumns([0])
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mLastCompletedActivities.ui'
        )

    def getColumnsIndexToSearch(self):
        return list(range(11))

    def fetchData(self):
        self.addRows(self.sap.getLastCompletedActivities())

    def addRows(self, data):
        self.clearAllItems()
        for d in data:  
            self.addRow(
                str(d['id']), 
                d['projeto_nome'], 
                d['lote'],
                d['fase_nome'], 
                d['subfase_nome'], 
                d['etapa_nome'], 
                d['bloco'],
                d['atividade_id'], 
                d['usuario'], 
                d['data_inicio'],
                d['data_fim'],
            )
        self.adjustColumns()

    def addRow(self, 
            primaryKey, 
            project, 
            lot,
            phase,
            subphase, 
            step, 
            block,
            activityId,
            user, 
            dataStart, 
            dataEnd
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(project))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(lot))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(phase))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(subphase))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(step))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(block))
        self.tableWidget.setItem(idx, 7, self.createNotEditableItem(activityId))
        self.tableWidget.setItem(idx, 8, self.createNotEditableItem(user))
        self.tableWidget.setItem(idx, 9, self.createNotEditableItem(dataStart))
        self.tableWidget.setItem(idx, 10, self.createNotEditableItem(dataEnd))

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
