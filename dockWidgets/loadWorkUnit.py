import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidget  import DockWidget
 
class LoadWorkUnit(DockWidget):

    def __init__(self, comboBoxPolygonLayer, controller):
        super(LoadWorkUnit, self).__init__(controller)
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.comboBoxPolygonLayer.currentIndexChanged.connect(self.updateAssociatedFields)
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        self.updateAssociatedFields(self.comboBoxPolygonLayer.currentIndex())
        self.loadProjects(self.controller.getSapStepsByTag(tag='projeto', sortByTag='projeto'))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "loadWorkUnit.ui"
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
            self.subphasesCb.clear()
            return
        self.loadProductionLines(self.projectsCb.currentText())

    def loadProductionLines(self, projectName):
        steps = self.controller.getSapStepsByTag(tag='linha_producao', sortByTag='linha_producao', tagFilter=('projeto', projectName))
        self.productionLinesCb.clear()
        self.productionLinesCb.addItem('...', None)
        for step in steps:
            self.productionLinesCb.addItem(step['linha_producao'], step['linha_producao_id'])
    
    @QtCore.pyqtSlot(int)
    def on_productionLinesCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.stepsCb.clear()
            self.subphasesCb.clear()
            return
        self.loadSteps(self.productionLinesCb.itemData(currentIndex))

    def loadSteps(self, productionLineId):
        steps = self.controller.getSapStepsByTag(tag='fase', sortByTag='fase', tagFilter=('linha_producao_id', productionLineId))
        self.stepsCb.clear()
        self.stepsCb.addItem('...', None)
        for step in steps:
            self.stepsCb.addItem("{0} {1}".format(step['fase'], step['ordem']), step['id'])
    
    @QtCore.pyqtSlot(int)
    def on_stepsCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.subphasesCb.clear()
            return
        self.loadSubphases(self.stepsCb.itemData(currentIndex))

    def loadSubphases(self, stepId):
        steps = self.controller.getSapStepsByTag(tag='subfase_id', sortByTag='subfase', tagFilter=('id', stepId))
        self.subphasesCb.clear()
        self.subphasesCb.addItem('...', None)
        for step in steps:
            self.subphasesCb.addItem(step['subfase'], step['subfase_id'])

    def updateAssociatedFields(self, currentIndex):
        if currentIndex < 0:
            return
        fields = self.comboBoxPolygonLayer.getCurrentLayerFields()
        for combo in [
                self.nameFieldCb,
                self.epsgFieldCb,
                self.obsFieldCb,
                self.dataIdFieldCb,
                self.lotIdFieldCb,
                self.availableFieldCb,
                self.priorityFieldCb 
            ]:
            combo.clear()
            combo.addItems(fields)

    def getAssociatedFields(self):
        return {
            'nome': self.nameFieldCb.currentText(),
            'epsg': self.epsgFieldCb.currentText(),
            'observacao': self.obsFieldCb.currentText(),
            'dado_producao_id': self.dataIdFieldCb.currentText(),
            'lote_id': self.lotIdFieldCb.currentText(),
            'disponivel': self.availableFieldCb.currentText(),
            'prioridade': self.priorityFieldCb.currentText()
        }

    def getSubphaseId(self):
        return self.subphasesCb.itemData(self.subphasesCb.currentIndex())

    def clearInput(self):
        pass

    def validInput(self):
        return self.comboBoxPolygonLayer.currentLayer()

    def runFunction(self):
        self.controller.loadWorkUnit(
            self.comboBoxPolygonLayer.currentLayer(),
            self.getSubphaseId(),
            self.onlySelectedCkb.isChecked(),
            self.getAssociatedFields()
        )