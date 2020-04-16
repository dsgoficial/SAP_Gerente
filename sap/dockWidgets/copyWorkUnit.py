import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class CopyWorkUnit(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(CopyWorkUnit, self).__init__(sapCtrl=sapCtrl)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        spacer = QtWidgets.QSpacerItem(20, 182, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacer)
        steps = self.sapCtrl.getSapStepsByTag(tag='projeto', sortByTag='projeto', tagFilter=('tipo_etapa_id', 2))
        self.loadProjects(steps)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "copyWorkUnit.ui"
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
            self.clearAllCheckBox()
            return
        self.loadProductionLines(self.projectsCb.currentText())

    def loadProductionLines(self, projectName):
        steps = self.sapCtrl.getSapStepsByTag(tag='linha_producao', sortByTag='linha_producao', tagFilter=('projeto', projectName))
        steps = [step for step in steps if step['tipo_etapa_id'] == 2]
        self.productionLinesCb.clear()
        self.productionLinesCb.addItem('...', None)
        for step in steps:
            self.productionLinesCb.addItem(step['linha_producao'], step['linha_producao_id'])
    
    @QtCore.pyqtSlot(int)
    def on_productionLinesCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.clearAllCheckBox()
            return
        self.loadSteps(self.productionLinesCb.itemData(currentIndex))

    def loadSteps(self, productionLineId):
        self.clearAllCheckBox()
        steps = self.sapCtrl.getSapStepsByTag(tag='id', sortByTag='fase', tagFilter=('linha_producao_id', productionLineId))
        steps = [ s for s in steps if s['tipo_fase_id'] != 3 ]
        for step in reversed(steps):
            print(step['fase'], step['id'])
            self.buildCheckBox("{0} {1}".format(step['fase'], step['ordem']), str(step['id']))

    def buildCheckBox(self, text, uuid):
        userCkb = QtWidgets.QCheckBox(text, self.scrollAreaWidgetContents)
        userCkb.setObjectName(uuid)
        self.verticalLayout.insertWidget(0, userCkb)

    def isCheckbox(self, widget):
        return type(widget) == QtWidgets.QCheckBox

    def getAllCheckBox(self):
        checkboxs = []
        for idx in range(self.verticalLayout.count()):
            widget = self.verticalLayout.itemAt(idx).widget()
            if not self.isCheckbox(widget):
                continue
            checkboxs.append(widget)
        return checkboxs

    def clearAllCheckBox(self):
        for checkbox in self.getAllCheckBox():
            checkbox.deleteLater()

    def getStepsIds(self):
        stepsIds = []
        for checkbox in self.getAllCheckBox():
            if not checkbox.isChecked():
               continue
            stepsIds.append(int(checkbox.objectName()))
        return stepsIds

    def clearInput(self):
        self.workspacesIdLe.setText('')

    def validInput(self):
        return (
            self.workspacesIdLe.text()
            and
            self.getStepsIds()
        )

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdLe.text().split(',') if d ]

    def runFunction(self):
        self.sapCtrl.copyWorkUnit(
            self.getWorkspacesIds(),
            self.getStepsIds(),
            self.associateInputsCkb.isChecked()

        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('copyWorkUnit', 'workUnit')
        self.workspacesIdLe.setText(values)