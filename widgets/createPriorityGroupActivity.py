import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class CreatePriorityGroupActivity(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(CreatePriorityGroupActivity, self).__init__(controller=sapCtrl)
        self.profiles = self.controller.getSapProductionProfiles()
        self.loadProfiles(self.profiles)
        self.setWindowTitle('Definir Atividades Prioritárias de Grupo')

    def loadProfiles(self, profiles):
        for profile in profiles:
            self.profilesCb.addItem(profile['nome'], profile['id'])

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
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def getProfileId(self):
        return self.profilesCb.itemData(self.profilesCb.currentIndex())

    def runFunction(self):
        self.controller.createSapPriorityGroupActivity(
            self.getActivitiesIds(),
            self.priorityLe.text(),
            self.getProfileId()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('createPriorityGroupActivity', 'activity')
        self.activityIdLe.setText(values)