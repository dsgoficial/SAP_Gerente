import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class AddNewRevision(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(AddNewRevision, self).__init__(controller=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "addNewRevision.ui"
        )

    def clearInput(self):
        self.workspacesIdLe.setText('')

    def validInput(self):
        return self.workspacesIdLe.text()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.addNewRevision(
            self.getWorkspacesIds()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('addNewRevision', 'workUnit')
        self.workspacesIdLe.setText(values)
        