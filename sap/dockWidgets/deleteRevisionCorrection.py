import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidget  import DockWidget
 
class DeleteRevisionCorrection(DockWidget):

    def __init__(self, sapCtrl):
        super(DeleteRevisionCorrection, self).__init__(sapCtrl=sapCtrl)
        #self.sapCtrl.getSapStepsByTypeId(2)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteRevisionCorrection.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def getUserId(self):
        for user in self.users:
            if user['nome'] == self.usersCb.currentText():
                return user['id']
        return False

    def runFunction(self):
        self.sapCtrl.getSapStepsByTypeId(2)
        """ self.sapCtrl.deleteUserActivities(
            self.getUserId()
        ) """