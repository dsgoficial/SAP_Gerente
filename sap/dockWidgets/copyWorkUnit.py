import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class CopyWorkUnit(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(CopyWorkUnit, self).__init__(sapCtrl=sapCtrl)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        spacer = QtWidgets.QSpacerItem(20, 182, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacer)
        self.loadSubphases(self.sapCtrl.getSapStepsByTag(tag='subfase'))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "copyWorkUnit.ui"
        )

    def loadSubphases(self, steps):
        self.subphasesCb.clear()
        self.subphasesCb.addItem('...', None)
        for step in steps:
            self.subphasesCb.addItem(step['subfase'], step['subfase_id'])
    
    @QtCore.pyqtSlot(int)
    def on_subphasesCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.clearAllCheckBox()
            return
        self.loadSteps(self.subphasesCb.itemData(currentIndex))

    def loadSteps(self, subphaseId):
        self.clearAllCheckBox()
        steps = self.sapCtrl.getSapStepsByTag(tag='id', numberTag='fase', sortByTag='fase', tagFilter=('subfase_id', subphaseId))
        steps = [ s for s in steps if s['tipo_fase_id'] != 3 ]
        for step in reversed(steps):
            self.buildCheckBox(step['fase'], str(step['id']))

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