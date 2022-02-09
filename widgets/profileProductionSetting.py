import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.managementDialogV2  import ManagementDialogV2

class ProfileProductionSetting(ManagementDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, parent=None):
        super(ProfileProductionSetting, self).__init__(controller, parent)
        self.setWindowTitle('Editar Configuração de Perfis')
        self.editProfileBtn.setIcon(QtGui.QIcon( self.getEditIconPath() ))
        self.editProfileBtn.setFixedSize(QtCore.QSize(28, 28))
        self.editProfileBtn.setIconSize(QtCore.QSize(20, 20))
        self.addSettingBtn.setEnabled(False)
        self.profileCb.currentIndexChanged.connect(self.updateWidgets)
        self.hiddenColumns([0,1,2])

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
        profileId = self.getProfileId()
        data = self.getController().getSapProfileProductionStep()
        self.addRows(filter(lambda d: d['perfil_producao_id'] == profileId, data))

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
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(subphaseId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(stepTypeId))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(subphase))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(stepType))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(priority))
        self.tableWidget.setCellWidget(
            idx, 
            6, 
            self.createRowEditWidget(
                self.tableWidget,
                idx, 
                6, 
                self.handleEditBtn, 
                self.handleDeleteBtn
            )
        )

    def addRows(self, data):
        self.clearAllTableItems(self.tableWidget)
        for d in data:  
            self.addRow(
                str(d['id']),
                d['subfase_id'],
                d['tipo_etapa_id'],
                d['subfase'],
                d['tipo_etapa'],
                d['prioridade']
            )
        self.adjustTable()

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'subfase_id': int(self.tableWidget.model().index(rowIndex, 1).data()),
            'tipo_etapa_id': int(self.tableWidget.model().index(rowIndex, 2).data()),
            'prioridade': int(self.tableWidget.model().index(rowIndex, 5).data())
        }