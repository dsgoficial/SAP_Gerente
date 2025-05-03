import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from .inputDialogV2  import InputDialogV2 
from functools import cmp_to_key

class LoadWorkUnit(InputDialogV2):

    def __init__(self, comboBoxPolygonLayer, sapCtrl):
        super(LoadWorkUnit, self).__init__(controller=sapCtrl)
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.comboBoxPolygonLayer.currentIndexChanged.connect(self.updateAssociatedFields)
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        self.updateAssociatedFields(self.comboBoxPolygonLayer.currentIndex())
        #self.loadProjects(self.controller.getSapStepsByTag(tag='projeto', sortByTag='projeto'))
        self.loadProjects(self.controller.getSapProjects())
        self.setWindowTitle('Carregar Unidades de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "loadWorkUnit.ui"
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
            self.productionLinesCb.clear()
            return
        self.loadProductionLines(self.lotsCb.itemData(currentIndex))
    
    def loadProductionLines(self, lotId):
        steps = self.controller.getSapStepsByTag(tag='linha_producao', sortByTag='linha_producao', tagFilter=('lote_id', lotId))
        self.productionLinesCb.clear()
        self.productionLinesCb.addItem('...', None)
        for step in steps:
            if not step['linha_producao_ativa']:
                continue
            self.productionLinesCb.addItem(step['linha_producao'], step['linha_producao_id'])
    
    @QtCore.pyqtSlot(int)
    def on_productionLinesCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.phasesCb.clear()
            return
        self.loadPhases(self.productionLinesCb.itemData(currentIndex))

    def loadPhases(self, productionLineId):
        steps = self.controller.getSapStepsByTag(tag='fase', tagFilter=('linha_producao_id', productionLineId))
        self.phasesCb.clear()
        self.phasesCb.addItem('...', None)
        for step in steps:
            self.phasesCb.addItem("{0} {1}".format(step['ordem_fase'], step['fase']), step['fase_id'])
    
    @QtCore.pyqtSlot(int)
    def on_phasesCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.clearAllCheckBox()
            return
        self.loadSubphases(self.phasesCb.itemData(currentIndex))

    def loadSubphases(self, phaseId):
        self.clearAllCheckBox()
        subphases = self.controller.getSapStepsByTagV2(tag='subfase_id', sortByTag='subfase', tagFilter=('fase_id', phaseId))
        print(f"Número de subfases encontradas: {len(subphases)}")
        subphases.sort(key=lambda item: int(item['subfase_id']), reverse=True)  
        for item in subphases:
            self.buildCheckBox("{}".format(item['subfase']), str(item['subfase_id']))

    def buildCheckBox(self, text, uuid):
        userCkb = QtWidgets.QCheckBox(text, self.scrollAreaWidgetContents)
        userCkb.setObjectName(uuid)
        self.scrollAreaWidgetContents.layout().insertWidget(0, userCkb)

    def isCheckbox(self, widget):
        return type(widget) == QtWidgets.QCheckBox

    def getAllCheckBox(self):
        checkboxs = []
        for idx in range(self.scrollAreaWidgetContents.layout().count()):
            widget = self.scrollAreaWidgetContents.layout().itemAt(idx).widget()
            if not self.isCheckbox(widget):
                continue
            checkboxs.append(widget)
        return checkboxs

    def clearAllCheckBox(self):
        for checkbox in self.getAllCheckBox():
            checkbox.deleteLater()

    def getSubphasesIds(self):
        subphasesIds = []
        for checkbox in self.getAllCheckBox():
            if not checkbox.isChecked():
               continue
            subphasesIds.append(int(checkbox.objectName()))
        return subphasesIds

    def updateAssociatedFields(self, currentIndex):
        if currentIndex < 0:
            return
        fields = self.comboBoxPolygonLayer.getCurrentLayerFields()
        for setting in [
                {
                    'combo': self.nameFieldCb,
                    'fields': [''] + fields,
                    'default': 'nome'
                },
                {
                    'combo': self.epsgFieldCb,
                    'fields': [''] + fields,
                    'default': 'epsg'
                },
                {
                    'combo': self.obsFieldCb,
                    'fields': [''] + fields,
                    'default': 'observacao'
                },
                {
                    'combo': self.dataIdFieldCb,
                    'fields': [''] + fields,
                    'default': 'dado_producao_id'
                },
                {
                    'combo': self.blockIdFieldCb,
                    'fields': [''] + fields,
                    'default': 'bloco_id'
                },
                {
                    'combo': self.availableFieldCb,
                    'fields': [''] + fields,
                    'default': 'disponivel'
                },
                {
                    'combo': self.priorityFieldCb,
                    'fields': [''] + fields,
                    'default': 'prioridade'
                },
                {
                    'combo': self.difficultyCb,
                    'fields': [''] + fields,
                    'default': 'dificuldade'
                },
                {
                    'combo': self.timeCb,
                    'fields': [''] + fields,
                    'default': 'tempo_estimado_minutos'
                }
            ]:
            combo = setting['combo']
            combo.clear()
            fieldSorted = sorted(setting['fields'], key=cmp_to_key(lambda a, b: 1 if b == setting['default'] else -1))
            if fieldSorted[0] != setting['default']:
                fieldSorted = sorted(setting['fields'], key=cmp_to_key(lambda a, b: 1 if b == '' else -1))
            combo.addItems(fieldSorted)

    def getAssociatedFields(self):
        return {
            'nome': self.nameFieldCb.currentText(),
            'epsg': self.epsgFieldCb.currentText(),
            'observacao': self.obsFieldCb.currentText(),
            'dado_producao_id': self.dataIdFieldCb.currentText(),
            'bloco_id': self.blockIdFieldCb.currentText(),
            'disponivel': self.availableFieldCb.currentText(),
            'prioridade': self.priorityFieldCb.currentText(),
            'dificuldade': self.difficultyCb.currentText(),
            'tempo_estimado_minutos': self.timeCb.currentText()
        }

    def getSubphaseId(self):
        return self.subphasesCb.itemData(self.subphasesCb.currentIndex())

    def getLotId(self):
        return self.lotsCb.itemData(self.lotsCb.currentIndex())

    def validInput(self):
        return self.comboBoxPolygonLayer.currentLayer()

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.okBtn.setEnabled(False)
        self.controller.loadSapWorkUnits(
            self.comboBoxPolygonLayer.currentLayer(),
            self.getLotId(),
            self.getSubphasesIds(),
            self.onlySelectedCkb.isChecked(),
            self.getAssociatedFields()
        )
        self.okBtn.setEnabled(True)
        QtWidgets.QApplication.restoreOverrideCursor()