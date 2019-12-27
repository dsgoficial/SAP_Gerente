import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.views.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete

 
class UnlockWorkspace(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(UnlockWorkspace, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis', 
            "unlockWorkspace.ui"
        )

    def validInput(self):
        return  self.workspaces_ids_le.text()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspaces_ids_le.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.unlockWorkspace(
            self.getWorkspacesIds()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('unlockWorkspace', 'workUnit')
        self.workspaces_ids_le.setText(values)