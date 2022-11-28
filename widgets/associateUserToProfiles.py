import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2
import json
from .addUserProfileProduction import AddUserProfileProduction

class AssociateUserToProfiles(MDialogV2):

    def __init__(
            self, 
            controller, qgis, sap,
            parent=None,
            AddUserProfileProduction=AddUserProfileProduction
        ):
        super(AssociateUserToProfiles, self).__init__(controller, parent)
        self.sap = sap
        self.setWindowTitle('Associar Usuários para Perfis')
        self.hiddenColumns([0, 3])
        self.users = None
        self.profiles = None
        self.AddUserProfileProduction = AddUserProfileProduction
        self.userProfileDlg = None
        self.setWindowTitle('Associar usuários à perfis produção')
        self.setUsers( self.sap.getUsers() )
        self.setProfiles( self.sap.getProductionProfiles() )
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'associateUserToProfiles.ui'
        )

    def setUsers(self, users):
        self.users = users

    def getUsers(self):
        return self.users

    def getUser(self, userId):
        return next(filter(lambda item: item['id'] == userId, self.users), None)

    def setProfiles(self, profiles):
        self.profiles = profiles

    def getProfiles(self):
        return self.profiles

    def getProfile(self, profileId):
        return next(filter(lambda item: item['id'] == profileId, self.profiles), None)

    def fetchData(self):
        data = self.getController().getSapUserProfileProduction()
        self.addRows(data)

    def addRows(self, data):
        self.clearAllTableItems(self.tableWidget)
        for d in data:  
            self.addRow(
                str(d['id']),
                d['usuario_id'],
                d['perfil_producao_id'],
                d
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            userId,
            profileId,
            dump
        ):
        idx = self.getRowIndex(str(primaryKey))
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        user = self.getUser(userId)
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem('{} {}'.format(user['tipo_posto_grad'], user['nome'])))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(self.getProfile(profileId)['nome']))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(json.dumps(dump)))
        optionColumn = 4
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
        self.userProfileDlg.close() if self.userProfileDlg else self.userProfileDlg
        self.userProfileDlg = self.AddUserProfileProduction(
            self.sap,
            self.controller,
            self.getUsers(),
            self.getProfiles()
        )
        self.userProfileDlg.activeEditMode(True)
        self.userProfileDlg.setData(data)
        self.userProfileDlg.accepted.connect(self.fetchData)
        self.userProfileDlg.show()

        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        self.getController().deleteSapUserProfileProduction([data['id']], self)
        self.fetchData()

    @QtCore.pyqtSlot(bool)
    def on_addProfileBtn_clicked(self):
        self.userProfileDlg.close() if self.userProfileDlg else self.userProfileDlg
        self.userProfileDlg = self.AddUserProfileProduction(
            self.sap,
            self.controller,
            self.getUsers(),
            self.getProfiles(),
            self
        )
        self.userProfileDlg.accepted.connect(self.fetchData)
        self.userProfileDlg.show()

    def getRowData(self, rowIndex):
        return json.loads(self.tableWidget.model().index(rowIndex, 3).data())