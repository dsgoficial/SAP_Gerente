import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class DeleteWorkUnitActivities(DockWidgetAutoComplete):

    def __init__(self, controller, sap):
        super(DeleteWorkUnitActivities, self).__init__(controller=controller)
        self.sap = sap
        self.setWindowTitle('Deletar Atividades de Unidade de Trabalhos')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteWorkUnitActivities.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')

    def validInput(self):
        return self.activityIdLe.text()

    def getLayersIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.sap.deleteWorkUnitActivities(
            self.getLayersIds()
        )
        self.showInfoMessageBox('Aviso', 'Realizado com sucesso!')
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('deleteWorkUnitActivities', 'workUnit')
        self.activityIdLe.setText(values)
        