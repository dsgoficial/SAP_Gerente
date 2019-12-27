import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.views.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class ReturnActivityToPreviousStep(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(ReturnActivityToPreviousStep, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis', 
            "returnActivityToPreviousStep.ui"
        )

    def validInput(self):
        return  self.activity_id_le.text()

    def getActivitiesIds(self):
        return [ int(d) for d in self.activity_id_le.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.returnActivityToPreviousStep(
            self.getActivitiesIds(),
            self.user_flag_ckb.isChecked()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('returnActivityToPreviousStep', 'activity')
        self.activity_id_le.setText(values)