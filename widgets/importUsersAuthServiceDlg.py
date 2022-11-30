import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
 
class ImportUsersAuthServiceDlg(QtWidgets.QDialog):

    def __init__(self, controller, qgis, sap):
        super(ImportUsersAuthServiceDlg, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.sap = sap
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.spacer = QtWidgets.QSpacerItem(20, 182, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem( self.spacer )
        self.loadUsers( self.sap.getUsersFromAuthService() )
        self.setWindowTitle('Importar Usuários')
        
    def loadUsers(self, users):
        self.cleanLayout()
        if len(users) == 0:
            self.showInfo('Aviso', 'Não há usuários!')
            return
        for user in users:
            self.buildCheckBox(
                '{0} {1} ({2})'.format(
                    user['tipo_posto_grad'],
                    user['nome_guerra'],
                    user['nome']
                ), 
                user['uuid']
            )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "importUsersAuthService.ui"
        )
    
    def buildCheckBox(self, text, uuid):
        userCkb = QtWidgets.QCheckBox(text, self.scrollAreaWidgetContents)
        userCkb.setObjectName(uuid)
        self.verticalLayout.insertWidget(0, userCkb)
    
    def isCheckbox(self, widget):
        return type(widget) == QtWidgets.QCheckBox

    def getAllCheckBox(self):
        checkboxs = []
        for idx in range(self.verticalLayout.count()):
            widget = self.verticalLayout.itemAt(idx).widget()
            if not self.isCheckbox(widget):
                continue
            checkboxs.append(widget)
        return checkboxs

    def cleanLayout(self):
        for checkbox in self.getAllCheckBox():
            checkbox.deleteLater()

    def getSelectedUsersIds(self):
        uuids = []
        for checkbox in self.getAllCheckBox():
            if not checkbox.isChecked():
               continue
            uuids.append(checkbox.objectName())
        return uuids

    def clearInput(self):
        for checkbox in self.getAllCheckBox():
            checkbox.setChecked(False)

    def validInput(self):
        return  self.getSelectedUsersIds()

    def runFunction(self):
        self.sap.importUsersAuthService(self.getSelectedUsersIds())
        self.loadUsers( self.sap.getUsersFromAuthService() )

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        self.runFunction()
        self.clearInput()
