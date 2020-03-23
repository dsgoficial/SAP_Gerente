import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class DeleteWorkUnits(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(DeleteWorkUnits, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteWorkUnits.ui"
        )

    def clearInput(self):
        self.workspacesIdLe.setText('')

    def validInput(self):
        return self.workspacesIdLe.text()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdLe.text().split(',') if d ]

    def runFunction(self):
        self.sapCtrl.deleteWorkUnits(
            self.getWorkspacesIds()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('deleteWorkUnits', 'workUnit')
        self.workspacesIdLe.setText(values)