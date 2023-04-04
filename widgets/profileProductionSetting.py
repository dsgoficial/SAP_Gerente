import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2

class ProfileProductionSetting(MDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, qgis, sap, parent):
        super(ProfileProductionSetting, self).__init__(controller, parent=parent)
        self.setWindowTitle('Editar Configuração de Perfis')
        self.sap = sap
        self.editProfileBtn.setIcon(QtGui.QIcon( self.getEditIconPath() ))
        self.editProfileBtn.setFixedSize(QtCore.QSize(28, 28))
        self.editProfileBtn.setIconSize(QtCore.QSize(20, 20))
        self.addSettingBtn.setEnabled(False)
        self.profileCb.currentIndexChanged.connect(self.updateWidgets)
        self.hiddenColumns([0,2,3])
        self.loadProfiles( controller.getSapProductionProfiles() )

    def updateWidgets(self, index):
        self.clearAllTableItems(self.tableWidget)
        self.addSettingBtn.setEnabled(False)
        profileId = self.getProfileId()
        if profileId is None:
            return
        self.addSettingBtn.setEnabled(True)
        self.updateSettingTable()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'profileProductionSetting.ui'
        )

    def loadProfiles(self, data):
        self.profileCb.clear()
        self.profileCb.addItem('...', None)
        for d in data:
            self.profileCb.addItem(d['nome'], d['id'])

    def getProfileId(self):
        return self.profileCb.itemData(self.profileCb.currentIndex())

    @QtCore.pyqtSlot(bool)
    def on_addSettingBtn_clicked(self):
        self.getController().openAddProfileProductionSetting(
            self,
            self.addSetting
        )

    def addSetting(self, data):
        data['perfil_producao_id'] = self.getProfileId()
        self.getController().createSapProfileProductionStep([data], self)
        self.updateSettingTable()

    def updateSetting(self, data):
        data['perfil_producao_id'] = self.getProfileId()
        self.getController().updateSapProfileProductionStep([data], self)
        self.updateSettingTable()

    def updateSettingTable(self):
        self.tableWidget.setSortingEnabled(False)
        profileId = self.getProfileId()
        data = self.getController().getSapProfileProductionStep()
        self.addRows(filter(lambda d: d['perfil_producao_id'] == profileId, data))
        self.tableWidget.setSortingEnabled(True)
        self.adjustTable()

    @QtCore.pyqtSlot(bool)
    def on_editProfileBtn_clicked(self):
        self.getController().openProductionProfileEditor(
            self,
            self.updateProfiles
        )

    def updateProfiles(self):
        self.loadProfiles(
            self.getController().getSapProductionProfiles()
        )
        self.save.emit()

    def getColumnsIndexToSearch(self):
        return []

    def handleEditBtn(self, index):
        self.getController().openEditProfileProductionSetting(
            self.getRowData(index.row()),
            self,
            self.updateSetting
        )
        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        self.getController().deleteSapProfileProductionStep([data['id']], self)
        self.updateSettingTable()

    def addRow(self, 
            primaryKey, 
            subphaseId,
            stepTypeId,
            subphase,
            stepType,
            priority
        ):
        idx = self.getRowIndex(str(primaryKey))
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(subphaseId))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(stepTypeId))
        self.tableWidget.setCellWidget(idx, 4, self.createLabel(subphase))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(stepType))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItemNumber(int(priority)))
        self.tableWidget.setCellWidget(
            idx, 
            1, 
            self.createRowEditWidget(
                self.tableWidget,
                idx, 
                1, 
                self.handleEditBtn, 
                self.handleDeleteBtn
            )
        )

    def addRows(self, data):
        self.clearAllTableItems(self.tableWidget)
        subphases = self.sap.getSubphases()
        for d in data:  
            subphase = next(filter(lambda item: item['subfase_id'] == d['subfase_id'], subphases), None)
            self.addRow(
                str(d['id']),
                d['subfase_id'],
                d['tipo_etapa_id'],
                "{} - {} - {}".format(subphase['linha_producao'], subphase['fase'], subphase['subfase']), 
                d['tipo_etapa'],
                d['prioridade']
            )
        self.adjustTable()

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'subfase_id': int(self.tableWidget.model().index(rowIndex, 2).data()),
            'tipo_etapa_id': int(self.tableWidget.model().index(rowIndex, 3).data()),
            'prioridade': int(self.tableWidget.model().index(rowIndex, 6).data())
        }