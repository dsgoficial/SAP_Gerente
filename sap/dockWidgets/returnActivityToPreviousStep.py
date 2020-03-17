import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class ReturnActivityToPreviousStep(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(ReturnActivityToPreviousStep, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "returnActivityToPreviousStep.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')

    def validInput(self):
        return  self.activityIdLe.text()

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.sapCtrl.returnActivityToPreviousStep(
            self.getActivitiesIds(),
            self.userFlagCkb.isChecked()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('returnActivityToPreviousStep', 'activity')
        self.activityIdLe.setText(values)