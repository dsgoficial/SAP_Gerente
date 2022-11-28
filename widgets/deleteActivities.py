import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class DeleteActivities(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(DeleteActivities, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Deletar Atividades')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteActivities.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')

    def validInput(self):
        return self.activityIdLe.text()

    def getLayersIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.deleteSapActivities(
            self.getLayersIds()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('deleteActivities', 'activity')
        self.activityIdLe.setText(values)
        