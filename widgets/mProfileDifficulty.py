import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.mDialogV2  import MDialogV2
import json
from .addProfileDifficulty import AddProfileDifficulty
from .addProfileDifficultyLot import AddProfileDifficultyLot

class MProfileDifficulty(MDialogV2):

    def __init__(
            self, 
            controller, qgis, sap,
            parent=None,
            AddProfileDifficulty=AddProfileDifficulty,
            AddProfileDifficultyLot=AddProfileDifficultyLot
        ):
        super(MProfileDifficulty, self).__init__(controller, parent)
        self.sap = sap
        self.hiddenColumns([0,5])
        self.users = None
        self.profiles = None
        self.AddProfileDifficulty = AddProfileDifficulty
        self.AddProfileDifficultyLot = AddProfileDifficultyLot
        self.profileDlg = None
        self.profileLotDlg = None
        self.setWindowTitle('Configurar Perfis de Finalização')
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mProfileDifficulty.ui'
        )

    def fetchData(self):
        self.tableWidget.setSortingEnabled(False)
        data = self.sap.getProfileDifficulty()
        self.addRows(data)
        self.tableWidget.setSortingEnabled(True)
        self.adjustTable()

    def addRows(self, data):
        self.clearAllTableItems(self.tableWidget)
        subphases = self.sap.getSubphases()
        for d in data:
            # SAP 3.0: a linha já traz a pessoa (posto e nome de guerra), o
            # tipo, a subfase e o lote pelo nome.
            subphase = next(filter(lambda item: item['subfase_id'] == d['subfase_id'], subphases), None)
            self.addRow(
                str(d['id']),
                "{} - {}".format(
                    d['usuario_posto'],
                    d['usuario_nome_guerra']
                ),
                d['tipo_perfil_dificuldade'],
                "{} - {}".format(
                    subphase['fase'],
                    subphase['subfase']
                ) if subphase else d['subfase'],
                d['lote'],
                d
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            user,
            profileDifficultyType,
            subphase,
            lot,
            dump
        ):
        idx = self.getRowIndex(str(primaryKey))
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(user))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(profileDifficultyType))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(lot))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(subphase))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(json.dumps(dump)))
        optionColumn = 6
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
        self.profileDlg = self.AddProfileDifficulty(
            self.sap,
            self
        )
        self.profileDlg.activeEditMode(True)
        self.profileDlg.setData(data)
        self.profileDlg.accepted.connect(self.fetchData)
        self.profileDlg.show()
        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        message = self.sap.deleteProfileDifficulty([data['id']])
        message and self.showInfo('Aviso', message)
        self.fetchData()

    @QtCore.pyqtSlot(bool)
    def on_addProfileBtn_clicked(self):
        self.profileDlg.close() if self.profileDlg else self.profileDlg
        self.profileDlg = self.AddProfileDifficulty(
            self.sap,
            self
        )
        self.profileDlg.accepted.connect(self.fetchData)
        self.profileDlg.show()

    def getRowData(self, rowIndex):
        return json.loads(self.tableWidget.model().index(rowIndex, 5).data())

    @QtCore.pyqtSlot(bool)
    def on_copyBtn_clicked(self):
        if not self.getSelected():
            self.showInfo('Aviso', 'Selecione as linhas!')
            return
        self.profileLotDlg.close() if self.profileLotDlg else None
        self.profileLotDlg = AddProfileDifficultyLot(
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