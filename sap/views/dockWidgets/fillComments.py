import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.views.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class FillComments(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(FillComments, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis', 
            "fillComments.ui"
        )

    def validInput(self):
        return  self.activity_id_le.text()

    def getActivitiesIds(self):
        return [ int(d) for d in self.activity_id_le.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.fillCommentActivity(
            self.getActivitiesIds(),
            self.obs_activity_le.text(),
            self.obs_workspace_le.text(),
            self.obs_step_le.text(),
            self.obs_subfase_le.text()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getFieldValuesLayerByFunction('fillComments')
        self.activity_id_le.setText(values)
