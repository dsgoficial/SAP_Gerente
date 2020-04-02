import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidget  import DockWidget
 
class  ResetPrivileges(DockWidget):

    def __init__(self, sapCtrl):
        super(ResetPrivileges, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "resetPrivileges.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def runFunction(self):
        self.sapCtrl.resetPrivileges()