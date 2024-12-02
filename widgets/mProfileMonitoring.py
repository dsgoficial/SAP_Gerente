import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
import json
from .addProfileMonitoring import AddProfileMonitoring
from .addProfileMonitoringLot import AddProfileMonitoringLot

class MProfileMonitoring(MDialogV2):

    def __init__(
            self, 
            controller, qgis, sap,
            parent=None,
            AddProfileMonitoring=AddProfileMonitoring,
            AddProfileMonitoringLot=AddProfileMonitoringLot
        ):
        super(MProfileMonitoring, self).__init__(controller, parent)
        self.sap = sap
        self.hiddenColumns([4])
        self.users = None
        self.profiles = None
        self.AddProfileMonitoring = AddProfileMonitoring
        self.AddProfileMonitoringLot = AddProfileMonitoringLot
        self.profileDlg = None
        self.profileLotDlg = None
        self.setWindowTitle('Configurar Perfis de Monitoramento')
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mProfileMonitoring.ui'
        )

    def fetchData(self):
        self.tableWidget.setSortingEnabled(False)
        data = self.sap.getMonitoringProfiles()
        self.addRows(data)
        self.tableWidget.setSortingEnabled(True)
        self.adjustTable()

    def addRows(self, data):
        self.clearAllTableItems(self.tableWidget)
        subphases = self.sap.getSubphases()
        lots = self.sap.getAllLots()
        for d in data:  
            lot = next(filter(lambda item: item['id'] == d['lote_id'], lots), None)
            subphase = next(filter(lambda item: item['subfase_id'] == d['subfase_id'], subphases), None)
            self.addRow(
                str(d['id']),
                d['tipo_monitoramento'],
                "{} - {}".format(
                    subphase['fase'],
                    subphase['subfase']
                ), 
                lot['nome_abrev'],
                d
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            monitoringType,
            subphase,
            lot,
            dump
        ):
        idx = self.getRowIndex(str(primaryKey))
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(monitoringType))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(lot))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(subphase))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(json.dumps(dump)))
        optionColumn = 5
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
        self.profileDlg.close() if self.profileDlg else self.profileDlg
        self.profileDlg = self.AddProfileMonitoring(
            self.sap,
            self
        )
        self.profileDlg.activeEditMode(True)
        self.profileDlg.setData(data)
        self.profileDlg.accepted.connect(self.fetchData)
        self.profileDlg.show()
        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        message = self.sap.deleteMonitoringProfiles([data['id']])
        message and self.showInfo('Aviso', message)
        self.fetchData()

    @QtCore.pyqtSlot(bool)
    def on_addProfileBtn_clicked(self):
        self.profileDlg.close() if self.profileDlg else self.profileDlg
        self.profileDlg = self.AddProfileMonitoring(
            self.sap,
            self
        )
        self.profileDlg.accepted.connect(self.fetchData)
        self.profileDlg.show()

    def getRowData(self, rowIndex):
        return json.loads(self.tableWidget.model().index(rowIndex, 4).data())

    @QtCore.pyqtSlot(bool)
    def on_copyBtn_clicked(self):
        if not self.getSelected():
            self.showInfo('Aviso', 'Selecione as linhas!')
            return
        self.profileLotDlg.close() if self.profileLotDlg else None
        self.profileLotDlg = AddProfileMonitoringLot(
            self.sap,
            self.getSelected(),
            self
        )
        self.profileLotDlg.accepted.connect(self.fetchData)
        self.profileLotDlg.show()

    def getSelected(self):
        rows = []
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if self.getRowData(qModelIndex.row())['id']:
                rows.append(self.getRowData(qModelIndex.row()))
        return rows