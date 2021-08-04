import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class AdvanceActivityToNextStep(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(AdvanceActivityToNextStep, self).__init__(controller=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "advanceActivityToNextStep.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')
        self.finishFlagCkb.setChecked(False)

    def validInput(self):
        return self.activityIdLe.text()

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.advanceSapActivityToNextStep(
            self.getActivitiesIds(),
            self.finishFlagCkb.isChecked()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('advanceActivityToNextStep', 'activity')
        self.activityIdLe.setText(values)