import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidget  import DockWidget
 
class ImportUsersAuthService(DockWidget):

    def __init__(self, controller):
        super(ImportUsersAuthService, self).__init__(controller)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        spacer = QtWidgets.QSpacerItem(20, 182, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacer)
        self.users = self.controller.getSapUsersFromAuthService()
        for user in self.users:
            self.buildCheckBox(user['nome'], user['uuid'])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
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
        self.controller.importSapUsersAuthService(self.getSelectedUsersIds())