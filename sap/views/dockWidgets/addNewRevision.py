import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.views.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class AddNewRevision(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(AddNewRevision, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis', 
            "addNewRevision.ui"
        )

    def validInput(self):
        return self.workspaces_id_le.text()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspaces_id_le.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.addNewRevision(
            self.getWorkspacesIds()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getFieldValuesLayerByFunction('addNewRevision')
        self.workspaces_id_le.setText(values)
        