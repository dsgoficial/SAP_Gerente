import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class OpenActivity(DockWidgetAutoComplete):

    def __init__(self, controller):
        super(OpenActivity, self).__init__(controller)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "openActivity.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')

    def validInput(self):
        return  self.activityIdLe.text()

    def getActivityId(self):
        return int(self.activityIdLe.text())

    def runFunction(self):
        self.controller.openSapActivity(
            self.getActivityId()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('openActivity', 'activity')
        self.activityIdLe.setText(values)