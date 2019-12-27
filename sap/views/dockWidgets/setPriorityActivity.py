import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.views.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class SetPriorityActivity(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(SetPriorityActivity, self).__init__(sapCtrl=sapCtrl)
        self.users = self.sapCtrl.getSapUsers()
        self.users_cb.addItems(sorted([ user['nome'] for user in self.users]))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis', 
            "setPriorityActivity.ui"
        )

    def validInput(self):
        return  self.activity_id_le.text() and self.priority_le.text() and self.getUserId()

    def getPritority(self):
        return int(self.priority_le.text())

    def getUserId(self):
        for user in self.users:
            if user['nome'] == self.users_cb.currentText():
                return user['id']

    def getActivitiesIds(self):
        return [ int(d) for d in self.activity_id_le.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.setPriorityActivity(
            self.getActivitiesIds(),
            self.getPritority(),
            self.getUserId()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('setPriorityActivity', 'activity')
        self.activity_id_le.setText(values)