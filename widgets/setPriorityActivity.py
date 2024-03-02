import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class SetPriorityActivity(DockWidgetAutoComplete):

    def __init__(self, controller, qgis, sap):
        super(SetPriorityActivity, self).__init__(controller=controller)
        self.setWindowTitle('Definir Atividades Prioritárias')
        self.sap = sap
        self.loadUsers( self.sap.getActiveUsers() )

    def loadUsers(self, users):
        for user in sorted(
                    users, 
                    key=lambda user: '{0} {1}'.format(user['tipo_posto_grad'], user['nome_guerra'])
                ):
            self.usersCb.addItem(
                '{0} {1}'.format(user['tipo_posto_grad'], user['nome_guerra']), 
                user['id']
            )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "setPriorityActivity.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')
        self.priorityLe.setText('')

    def validInput(self):
        return  self.activityIdLe.text() and self.priorityLe.text() and self.getUserId()

    def getPritority(self):
        return int(self.priorityLe.text())

    def getUserId(self):
        return self.usersCb.itemData(self.usersCb.currentIndex())

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.setSapPriorityActivity(
            self.getActivitiesIds(),
            self.getPritority(),
            self.getUserId()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('setPriorityActivity', 'activity')
        self.activityIdLe.setText(values)