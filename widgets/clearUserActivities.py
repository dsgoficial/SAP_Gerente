import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class ClearUserActivities(DockWidget):

    def __init__(self, users, sapCtrl):
        super(ClearUserActivities, self).__init__(controller=sapCtrl)
        self.users = users
        self.usersCb.addItems(sorted([ '{0} {1}'.format(user['tipo_posto_grad'], user['nome_guerra']) for user in self.users]))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "clearUserActivities.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  self.getUserId()

    def getUserId(self):
        for user in self.users:
            if user['nome'] == self.usersCb.currentText():
                return user['id']
        return False

    def runFunction(self):
        self.controller.deleteUserActivities(
            self.getUserId()
        )