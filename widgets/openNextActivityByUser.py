import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class OpenNextActivityByUser(DockWidget):

    def __init__(self, users, sapCtrl):
        super(OpenNextActivityByUser, self).__init__(controller=sapCtrl)
        self.users = users
        self.usersCb.addItems(sorted([ user['nome'] for user in self.users]))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "openNextActivityByUser.ui"
        )

    def clearInput(self):
        self.nextActivityCkb.setChecked(False)

    def validInput(self):
        return  self.getUserId()

    def getUserId(self):
        for user in self.users:
            if user['nome'] == self.usersCb.currentText():
                return user['id']
        return False

    def runFunction(self):
        self.controller.openNextActivityByUser(
            self.getUserId(),
            self.nextActivityCkb.isChecked()
        )