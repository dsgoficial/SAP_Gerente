import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class DeleteAssociatedInputs(DockWidgetAutoComplete):

    def __init__(self, inputGroups, sapCtrl):
        super(DeleteAssociatedInputs, self).__init__(sapCtrl=sapCtrl)
        self.loadInputGroups(inputGroups)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteAssociatedInputs.ui"
        )
    
    def loadInputGroups(self, inputGroupsData):
        self.inputGroupsCb.clear()
        #self.inputGroupsCb.addItem('...', None)
        for inputData in inputGroupsData:
            self.inputGroupsCb.addItem(inputData['nome'], inputData['id'])

    def getInputGroupId(self):
        return self.inputGroupsCb.itemData(self.inputGroupsCb.currentIndex())

    def clearInput(self):
        self.workspacesIdLe.setText('')
        #self.inputGroupsCb.setCurrentIndex(0)

    def validInput(self):
        return self.workspacesIdLe.text()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdLe.text().split(',') if d ]

    def runFunction(self):
        self.sapCtrl.deleteAssociatedInputs(
            self.getWorkspacesIds(),
            self.getInputGroupId()
        )
      
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('deleteAssociatedInputs', 'workUnit')
        self.workspacesIdLe.setText(values)