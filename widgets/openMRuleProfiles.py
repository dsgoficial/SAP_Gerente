import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
 
class OpenMRuleProfiles(DockWidget):

    def __init__(self, sapCtrl):
        super(OpenMRuleProfiles, self).__init__(controller=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "openManagement.ui"
        )

    def clearInput(self):
        pass
        
    def validInput(self):
        return  True

    def runFunction(self):
        self.controller.openMRuleProfiles()