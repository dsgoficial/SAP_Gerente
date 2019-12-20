import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.views.dockWidgets.dockWidget  import DockWidget
 
class OpenManagementModels(DockWidget):

    def __init__(self, sapCtrl):
        super(OpenManagementModels, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis', 
            "openManagement.ui"
        )

    def validInput(self):
        return  True

    def runFunction(self):
        self.sapCtrl.openManagementModels()