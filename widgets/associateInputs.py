import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class AssociateInputs(DockWidgetAutoComplete):

    def __init__(self, inputGroups, sapCtrl):
        super(AssociateInputs, self).__init__(controller=sapCtrl)
        self.loadInputGroups(inputGroups)
        self.loadAssociationStrategies(self.controller.getSapAssociationStrategies())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "associateInputs.ui"
        )
    
    def loadInputGroups(self, inputGroupsData):
        self.inputGroupsCb.clear()
        for inputData in inputGroupsData:
            self.inputGroupsCb.addItem(inputData['nome'], inputData['id'])

    def loadAssociationStrategies(self, strategiesData):
        self.associationStrategyCb.clear()
        for data in strategiesData:
            self.associationStrategyCb.addItem(data['nome'], data['code'])

    def getInputGroupId(self):
        return self.inputGroupsCb.itemData(self.inputGroupsCb.currentIndex())

    def getAssociationStrategyId(self):
        return self.associationStrategyCb.itemData(self.associationStrategyCb.currentIndex())

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdLe.text().split(',') if d ]

    def clearInput(self):
        self.workspacesIdLe.setText('')
        self.defaultPathCb.setText('')

    def validInput(self):
        return (
            self.workspacesIdLe.text()
        )

    def runFunction(self):
        self.controller.associateInputs(
            self.getWorkspacesIds(), 
            self.getInputGroupId(), 
            self.getAssociationStrategyId(), 
            self.defaultPathCb.text()
        )
      
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('associateInputs', 'workUnit')
        self.workspacesIdLe.setText(values)