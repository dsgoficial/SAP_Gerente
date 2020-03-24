import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidget  import DockWidget
 
class DeleteRevisionCorrection(DockWidget):

    def __init__(self, sapCtrl):
        super(DeleteRevisionCorrection, self).__init__(sapCtrl=sapCtrl)
        self.loadSteps(self.sapCtrl.getSapStepsByTypeId(2))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteRevisionCorrection.ui"
        )

    def clearInput(self):
        self.stepsCb.setCurrentIndex(0)

    def validInput(self):
        return  self.getStepId()

    def loadSteps(self, steps):
        self.stepsCb.clear()
        self.stepsCb.addItem('...', None)
        for step in steps:
            self.stepsCb.addItem(step['subfase'], step['id'])

    def getStepId(self):
        return self.stepsCb.itemData(self.stepsCb.currentIndex())

    def runFunction(self):
        self.sapCtrl.deleteRevisionCorrection(self.getStepId())