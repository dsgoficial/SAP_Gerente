import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class CopyWorkUnit(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(CopyWorkUnit, self).__init__(controller=sapCtrl)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        spacer = QtWidgets.QSpacerItem(20, 182, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacer)
        self.loadProjects(self.controller.getSapProjects())
        self.setWindowTitle('Copiar Unidades de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "copyWorkUnit.ui"
        )

    def loadProjects(self, data):
        self.projectsCb.clear()
        self.projectsCb.addItem('...', None)
        for d in data:
            self.projectsCb.addItem(d['nome'], d['id'])

    @QtCore.pyqtSlot(int)
    def on_projectsCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.lotsCb.clear()
            self.clearAllCheckBox()
            return
        self.loadLots(self.projectsCb.currentText())

    def loadLots(self, projectName):
        steps = self.controller.getSapStepsByTag(tag='lote', sortByTag='lote', tagFilter=('projeto', projectName))
        self.lotsCb.clear()
        self.lotsCb.addItem('...', None)
        for step in steps:
            self.lotsCb.addItem(step['lote'], step['lote_id'])
    
    @QtCore.pyqtSlot(int)
    def on_lotsCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.clearAllCheckBox()
            return
        self.loadSteps(self.lotsCb.itemData(currentIndex))

    def loadSteps(self, loteId):
        self.clearAllCheckBox()
        subphase = self.controller.getSapSubphases()
        subphase = [ s for s in subphase if s['lote_id'] == loteId ]
        subphase.sort(key=lambda item: int(item['subfase_id']), reverse=True)  
        for step in subphase:
            self.buildCheckBox(f"{step['fase']} - {step['subfase']}", str(step['subfase_id']))

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
        self.controller.copySapWorkUnit(
            self.getWorkspacesIds(),
            self.getStepsIds(),
            self.associateInputsCkb.isChecked()

        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('copyWorkUnit', 'workUnit')
        self.workspacesIdLe.setText(values)