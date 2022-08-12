import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class CreateActivities(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(CreateActivities, self).__init__(controller=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createActivities.ui"
        )

    def clearInput(self):
        self.workspacesIdsLe.setText('')
        self.stepsCb.clear()

    def validInput(self):
        return self.workspacesIdsLe.text() and self.getStepId()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdsLe.text().split(',') if d ]

    def getStepId(self):
        return int(self.stepsCb.itemData(self.stepsCb.currentIndex()))

    def runFunction(self):
        self.controller.createSapActivities(
            self.getWorkspacesIds(),
            self.getStepId()
        )
        
    def loadSteps(self):
        layersId = self.getWorkspacesIds()
        if not layersId:
            return
        steps = self.controller.getSapStepsByFeatureId(layersId[0])
        self.stepsCb.clear()
        self.stepsCb.addItem('...', None)
        for step in steps:
            self.stepsCb.addItem("{0} {1}".format(step['etapa'], step['ordem']), step['etapa_id'])
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('createActivities', 'activity')
        self.workspacesIdsLe.setText(values)
        self.loadSteps()
        