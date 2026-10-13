# -*- coding: utf-8 -*-
import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
from .addLotForm import AddLotForm
import json
from SAP_Gerente.modules.sap.api.contrato import emAndamento

class MLots(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addLotForm=AddLotForm
            ):
        if not sap.leAcervo():
            # SAP 3.0: projeto e lote são do ACERVO; ler e gravar cobra perfil
            # no módulo Acervo.
            raise Exception('Lotes: no SAP 3.0 projeto e lote são do Acervo, e esta tela exige perfil no módulo Acervo.')
        super(MLots, self).__init__(controller=controller)
        self.addLotForm = addLotForm
        self.qgis = qgis
        self.sap = sap
        self.addLotFormDlg = None
        self.tableWidget.setColumnHidden(9, True)
        self.showFinishedCheckBox.setChecked(False)
        self.showFinishedCheckBox.stateChanged.connect(self.fetchData)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mLots.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getAllLots()
        if not self.showFinishedCheckBox.isChecked():
            # Só os lotes não encerrados (SAP 3.0)
            data = [lot for lot in data if emAndamento(lot)]
        self.addRows(data)

    def addRows(self, data):
        self.clearAllItems()
        for row in data:
            # SAP 3.0 (acervo.lote): a linha já traz o projeto e o status pelo
            # nome; PIT e período no lugar de nome abreviado, escala e linha.
            self.addRow(
                row['id'],
                row['nome'],
                row.get('descricao') or '',
                row.get('pit') or '',
                str(row.get('data_inicio') or '')[:10],
                str(row.get('data_fim') or '')[:10],
                row['projeto'],
                row.get('status_execucao') or '',
                json.dumps(row)
            )
        self.adjustColumns()

    def addRow(self, 
            primaryKey, 
            name,
            description,
            pit,
            dataInicio,
            dataFim,
            project,
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
        self.tableWidget.setCellWidget(idx, 4, self.createLabelV2(pit, idx, 4))
        self.tableWidget.setCellWidget(idx, 5, self.createLabelV2(dataInicio, idx, 5))
        self.tableWidget.setCellWidget(idx, 6, self.createLabelV2(project, idx, 6))
        self.tableWidget.setCellWidget(idx, 7, self.createLabelV2(dataFim, idx, 7))
        self.tableWidget.setCellWidget(idx, 8, self.createLabelV2(status, idx, 8))
        self.tableWidget.setItem(idx, 9, self.createNotEditableItem(dump))
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
        self.addLotFormDlg.close() if self.addLotFormDlg else None
        self.addLotFormDlg = self.addLotForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addLotFormDlg.activeEditMode(True)
        self.addLotFormDlg.setData(data)
        self.addLotFormDlg.save.connect(self.fetchData)
        self.addLotFormDlg.show()

        
    def handleDeleteBtn(self, index):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir o lote?')
        if not result:
            return
        data = self.getRowData(index.row())
        try:
            message = self.sap.deleteLots([data['id']])
            message and self.showInfo('Aviso', message)
            self.fetchData()
        except Exception as e:
            self.showError('Aviso', str(e))

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return json.loads(self.tableWidget.model().index(rowIndex, 9).data())

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addLotFormDlg.close() if self.addLotFormDlg else None
        self.addLotFormDlg = self.addLotForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addLotFormDlg.save.connect(self.fetchData)
        self.addLotFormDlg.show()