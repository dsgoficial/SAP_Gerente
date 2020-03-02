import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class CreateActivities(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(CreateActivities, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createActivities.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')

    def validInput(self):
        return self.activityIdLe.text()

    def getLayersIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.createActivities(
            self.getLayersIds()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('createActivities', 'activity')
        self.activityIdLe.setText(values)
        