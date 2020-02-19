import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class CreatePriorityGroupActivity(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(CreatePriorityGroupActivity, self).__init__(sapCtrl=sapCtrl)
        self.profiles = self.sapCtrl.getSapProfiles()
        self.profilesCb.addItems(sorted([ profiles['nome'] for profiles in self.profiles]))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createPriorityGroupActivity.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')
        self.priorityLe.setText('')

    def validInput(self):
        return self.activityIdLe.text() and self.getProfileId() and self.priorityLe.text() 

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') ]

    def getProfileId(self):
        for profile in self.profiles:
            if profile['nome'] == self.profilesCb.currentText():
                return profile['id']

    def runFunction(self):
        self.sapCtrl.createPriorityGroupActivity(
            self.getActivitiesIds(),
            self.priorityLe.text(),
            self.getProfileId()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('createPriorityGroupActivity', 'activity')
        self.activityIdLe.setText(values)