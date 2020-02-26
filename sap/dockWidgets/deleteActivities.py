import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class DeleteActivities(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(DeleteActivities, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteActivities.ui"
        )

    def clearInput(self):
        self.layerIdLe.setText('')

    def validInput(self):
        return self.layerIdLe.text()

    def getLayersIds(self):
        return [ int(d) for d in self.layerIdLe.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.deleteActivities(
            self.getLayersIds()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('deleteActivities', 'layerId')
        self.layerIdLe.setText(values)
        