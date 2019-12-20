import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.views.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class CreatePriorityGroupActivity(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(CreatePriorityGroupActivity, self).__init__(sapCtrl=sapCtrl)
        self.profiles = self.sapCtrl.getSapProfiles()
        self.profiles_cb.addItems(sorted([ profiles['nome'] for profiles in self.profiles]))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis', 
            "createPriorityGroupActivity.ui"
        )

    def validInput(self):
        return self.activity_id_le.text() and self.getProfileId() and self.priority_le.text() 

    def getActivitiesIds(self):
        return [ int(d) for d in self.activity_id_le.text().split(',') ]

    def getProfileId(self):
        for profile in self.profiles:
            if profile['nome'] == self.profiles_cb.currentText():
                return profile['id']

    def runFunction(self):
        self.sapCtrl.createPriorityGroupActivity(
            self.getActivitiesIds(),
            self.priority_le.text(),
            self.getProfileId()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getFieldValuesLayerByFunction('createPriorityGroupActivity')
        self.activity_id_le.setText(values)