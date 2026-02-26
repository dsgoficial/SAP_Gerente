# -*- coding: utf-8 -*-
import os, json
from datetime import datetime, timezone
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2 import MDialogV2
from qgis.core import QgsGeometry
from SAP_Gerente.modules.qgis.mapFunctions.createTemporaryLayer import CreateTemporaryLayer
from SAP_Gerente.modules.qgis.factories.qgisApiSingleton import QgisApiSingleton


class AlteracaoFluxo(MDialogV2):

    def __init__(self, controller, qgis, sap):
        super(AlteracaoFluxo, self).__init__(controller=controller)
        self.sap = sap
        self.qgis = qgis
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(8, True)
        self.fetchTableData()
        self.onlyFixedCkb.stateChanged.connect(lambda state: self.fetchTableData())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'alteracaoFluxo.ui'
        )

    def getColumnsIndexToSearch(self):
        return [1, 2, 3, 4]

    def fetchTableData(self):
        self.addRows(self.sap.getAlteracaoFluxo())

    def addRows(self, data):
        self.clearAllItems()
        for d in data:
            if d['resolvido'] and not self.onlyFixedCkb.isChecked():
                continue
            self.addRow(
                d['id'],
                d['atividade_id'],
                d['usuario'],
                d['descricao'],
                self.formatDate(d['data']),
                d['resolvido'],
                d['geom'],
                json.dumps(d)
            )
        self.adjustColumns()

    def formatDate(self, isoString):
        if not isoString:
            return ''
        try:
            dt = datetime.fromisoformat(isoString.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y %H:%M')
        except Exception:
            return isoString

    def addRow(self, primaryKey, atividadeId, usuario, descricao, data, resolvido, geom, dump):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(atividadeId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(usuario))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(descricao))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(data))

        self.tableWidget.setCellWidget(
            idx,
            5,
            self.createCheckbox(
                resolvido,
                lambda state, rowId=primaryKey, rowDump=dump: self.setResolvido(state, rowId, rowDump)
            )
        )

        self.tableWidget.setCellWidget(
            idx,
            6,
            self.createButton(
                'Abrir',
                lambda b, aid=atividadeId: self.openActivity(aid)
            )
        )

        self.tableWidget.setCellWidget(
            idx,
            7,
            self.createButton(
                'Carregar',
                lambda b, g=geom: self.loadGeom(g)
            )
        )

        self.tableWidget.setItem(idx, 8, self.createNotEditableItem(dump))

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if primaryKey == self.tableWidget.model().index(idx, 0).data():
                return idx
        return -1

    def createCheckbox(self, checked, handle):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        ckb = QtWidgets.QCheckBox()
        ckb.setChecked(checked)
        ckb.stateChanged.connect(handle)
        layout.addWidget(ckb)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return wd

    def createButton(self, name, handle):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        btn = QtWidgets.QPushButton(name)
        btn.clicked.connect(handle)
        layout.addWidget(btn)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return wd

    def setResolvido(self, state, rowId, dump):
        d = json.loads(dump)
        payload = [{
            'id': d['id'],
            'atividade_id': d['atividade_id'],
            'descricao': d['descricao'],
            'data': d['data'],
            'resolvido': state == QtCore.Qt.Checked,
            'geom': d['geom']
        }]
        message = self.sap.atualizaAlteracaoFluxo(payload)
        message and self.showInfo('Aviso', message)
        self.fetchTableData()

    def openActivity(self, activityId):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.qgis.startSapFP(
            self.sap.getActivityDataById(activityId)
        )
        QtWidgets.QApplication.restoreOverrideCursor()

    def loadGeom(self, ewkt):
        if not ewkt:
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            srid = ewkt.split(';')[0].split('=')[1]
            wkt = ewkt.split(';')[1]
            temporaryLayer = CreateTemporaryLayer().run(
                'alteracao_fluxo',
                'polygon',
                ['id'],
                "EPSG:{}".format(srid)
            )
            qgisApi = QgisApiSingleton.getInstance()
            qgisApi.addFeature(temporaryLayer, {'id': 0}, QgsGeometry().fromWkt(wkt))
            qgisApi.addLayerOnMap(temporaryLayer)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def getRowData(self, rowIndex):
        return {}
