import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class DeleteWorkUnits(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(DeleteWorkUnits, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Deletar Unidades de Trabalho')

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
        self.controller.deleteSapWorkUnits(
            self.getWorkspacesIds()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('deleteWorkUnits', 'workUnit')
        self.workspacesIdLe.setText(values)