import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
import re

class SubphasesSelector(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(SubphasesSelector, self).__init__(parent=parent)
        uic.loadUi(self.getUiPath(), self)
        self.projects = []
        self.suphases = []
       
    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'subphasesSelector.ui'
        )

    def setup(self, projects, suphases):
        self.projects = projects
        self.suphases = suphases
        self.loadProjects(self.projects)

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
        steps = self.getStepsByTag(tag='lote', sortByTag='lote', tagFilter=('projeto', projectName))
        self.lotsCb.clear()
        self.lotsCb.addItem('...', None)
        for step in steps:
            self.lotsCb.addItem(step['lote'], step['lote_id'])

    def getStepsByTag(self, tag, withDuplicate=False, numberTag='', tagFilter=('', ''), sortByTag=''):
        def defaultOrder(elem):
            return elem['ordem_fase']
        def atoi(text):
            return int(text) if text.isdigit() else text
        def orderBy(elem):
            return [ atoi(c) for c in re.split(r'(\d+)', elem[sortByTag].lower()) ]
        steps = self.suphases
        steps.sort(key=defaultOrder)  
        if tagFilter[0] and tagFilter[1]:
            steps = [ s for s in steps if s[tagFilter[0]] == tagFilter[1]]   
        selectedSteps = []  
        for step in steps:
            value = step[tag]
            tagTest = [ t[tag] for t in selectedSteps if str(value).lower() in str(t[tag]).lower() ]
            if not(withDuplicate) and tagTest:
                continue
            if numberTag:
                number = len([ t for t in selectedSteps if str(step[numberTag]).lower() in str(t[numberTag]).lower() ]) + 1
                step[numberTag] = "{0} {1}".format(step[numberTag], number)
            selectedSteps.append(step)
        if sortByTag:
            selectedSteps.sort(key=orderBy)
        return selectedSteps
    
    @QtCore.pyqtSlot(int)
    def on_lotsCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.clearAllCheckBox()
            return
        self.loadSteps(self.lotsCb.itemData(currentIndex))

    def loadSteps(self, loteId):
        self.clearAllCheckBox()
        subphase = self.suphases
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