import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class PauseActivity(DockWidgetAutoComplete):

    def __init__(self, controller):
        super(PauseActivity, self).__init__(controller)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "pauseActivity.ui"
        )
    
    def clearInput(self):
        self.activityIdLe.setText('')

    def validInput(self):
        return  self.activityIdLe.text()

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.pauseActivity(
            self.getActivitiesIds()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('pauseActivity', 'activity')
        self.activityIdLe.setText(values)