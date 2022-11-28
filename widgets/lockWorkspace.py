import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class LockWorkspace(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(LockWorkspace, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Bloquear Unidades de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "lockWorkspace.ui"
        )

    def clearInput(self):
        self.workspacesIdsLe.setText('')

    def validInput(self):
        return  self.workspacesIdsLe.text()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdsLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.lockSapWorkspace(
            self.getWorkspacesIds()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('lockWorkspace', 'workUnit')
        self.workspacesIdsLe.setText(values)