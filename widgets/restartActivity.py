import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class RestartActivity(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(RestartActivity, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Reiniciar Atividade em Execução ou Pausadas')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "restartActivity.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')

    def validInput(self):
        return  self.activityIdLe.text()

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.restartSapActivity(
            self.getActivitiesIds()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('restartActivity', 'activity')
        self.activityIdLe.setText(values)