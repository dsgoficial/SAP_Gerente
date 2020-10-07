import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidget  import DockWidget
 
class DeleteRevisionCorrection(DockWidget):

    def __init__(self, controller):
        super(DeleteRevisionCorrection, self).__init__(controller)
        steps = self.controller.getSapStepsByTag(tag='projeto', sortByTag='projeto', tagFilter=('tipo_etapa_id', 2))
        #steps = [step for step in steps if step['tipo_etapa_id'] == 2]
        self.loadProjects(steps)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "deleteRevisionCorrection.ui"
        )

    def loadProjects(self, steps):
        self.projectsCb.clear()
        self.projectsCb.addItem('...', None)
        for step in steps:
            self.projectsCb.addItem(step['projeto'])

    @QtCore.pyqtSlot(int)
    def on_projectsCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.productionLinesCb.clear()
            self.stepsCb.clear()
            return
        self.loadProductionLines(self.projectsCb.currentText())

    def loadProductionLines(self, projectName):
        steps = self.controller.getSapStepsByTag(tag='linha_producao', sortByTag='linha_producao', tagFilter=('projeto', projectName))
        steps = [step for step in steps if step['tipo_etapa_id'] == 2]
        self.productionLinesCb.clear()
        self.productionLinesCb.addItem('...', None)
        for step in steps:
            self.productionLinesCb.addItem(step['linha_producao'], step['linha_producao_id'])
    
    @QtCore.pyqtSlot(int)
    def on_productionLinesCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.stepsCb.clear()
            return
        self.loadSteps(self.productionLinesCb.itemData(currentIndex))

    def loadSteps(self, productionLineId):
        steps = self.controller.getSapStepsByTag(tag='fase', sortByTag='fase', tagFilter=('linha_producao_id', productionLineId))
        steps = [step for step in steps if step['tipo_etapa_id'] == 2]
        self.stepsCb.clear()
        self.stepsCb.addItem('...', None)
        for step in steps:
            self.stepsCb.addItem("{0} {1}".format(step['fase'], step['ordem']), step['id'])

    def clearInput(self):
        self.stepsCb.setCurrentIndex(0)

    def validInput(self):
        return  self.getStepId()

    def getStepId(self):
        return self.stepsCb.itemData(self.stepsCb.currentIndex())

    def runFunction(self):
        self.controller.deleteSapRevisionCorrection(self.getStepId())