import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.managementDialogV2  import ManagementDialogV2

class AssociateUserToProfiles(ManagementDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(AssociateUserToProfiles, self).__init__(controller, parent)
        self.setWindowTitle('Associar Usuários para Perfis')
        self.userCb.currentIndexChanged.connect(self.updateWidgets)
        self.hiddenColumns([0, 1])

    def updateWidgets(self, index):
        self.clearAllTableItems(self.tableWidget)
        self.addProfileBtn.setEnabled(False)
        userId = self.getUserId()
        if userId is None:
            return
        self.addProfileBtn.setEnabled(True)
        self.updateProfileTable()


    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'associateUserToProfiles.ui'
        )

    def loadUsers(self, data):
        self.userCb.clear()
        self.userCb.addItem('...', None)
        for d in data:
            self.userCb.addItem(
                '{} {}'.format(d['tipo_posto_grad'], d['nome']), 
                d['id']
            )
    
    def getUserId(self):
        return self.userCb.itemData(self.userCb.currentIndex())

    @QtCore.pyqtSlot(bool)
    def on_addProfileBtn_clicked(self):
        self.getController().openAddUserProfileProduction(
            self.getUserId(),
            self,
            self.updateProfileTable
        )

    def updateProfileTable(self):
        userId = self.getUserId()
        data = self.getController().getSapUserProfileProduction()
        self.addRows(filter(lambda d: d['usuario_id'] == userId, data))

    def getColumnsIndexToSearch(self):
        return []

    def handleEditBtn(self, index):
        self.getController().openEditUserProfileProduction(
            self.getUserId(),
            self.getRowData(index.row()),
            self,
            self.updateProfileTable
        )
        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        self.getController().deleteSapUserProfileProduction([data['id']], self)
        self.updateProfileTable()

    def addRow(self, 
            primaryKey, 
            profileId,
            profile
        ):
        idx = self.getRowIndex(str(primaryKey))
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(profileId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(profile))
        optionColumn = 3
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

    def addRows(self, data):
        self.clearAllTableItems(self.tableWidget)
        for d in data:  
            self.addRow(
                str(d['id']),
                d['perfil_producao_id'],
                d['perfil_producao']
            )
        self.adjustTable()

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'perfil_producao_id': int(self.tableWidget.model().index(rowIndex, 1).data())
        }