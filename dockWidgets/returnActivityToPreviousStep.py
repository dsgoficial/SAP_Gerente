import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class ReturnActivityToPreviousStep(DockWidgetAutoComplete):

    def __init__(self, controller):
        super(ReturnActivityToPreviousStep, self).__init__(controller)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "returnActivityToPreviousStep.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')

    def validInput(self):
        return  self.activityIdLe.text()

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.returnSapActivityToPreviousStep(
            self.getActivitiesIds(),
            self.userFlagCkb.isChecked()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('returnActivityToPreviousStep', 'activity')
        self.activityIdLe.setText(values)