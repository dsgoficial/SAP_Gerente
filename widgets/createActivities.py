import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
import json

class CreateActivities(DockWidgetAutoComplete):

    def __init__(self, controller, qgis, sap):
        super(CreateActivities, self).__init__(controller=controller)
        self.setWindowTitle('Criar Atividades')
        self.qgis = qgis
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createActivities.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return self.getWorkspacesIds() and self.getStepIds()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdsLe.text().split(',') if d ]

    def runFunction(self):
        self.sap.createActivities({
            'unidade_trabalho_ids': self.getWorkspacesIds(),
            'etapa_ids': self.getStepIds()
        })    
        
    def loadSteps(self):
        layersId = self.getWorkspacesIds()
        if not layersId:
            return
        try:
            steps = self.getSapStepsByFeatureId(layersId)
        except Exception as e:
            self.controller.showErrorMessageBox(
                parent=self, title='Aviso', message=str(e)
            )
            self.stepsCb.clear()
            self.workspacesIdsLe.setText('')
            return
        steps.sort(key=lambda item: int(item['ordem']))  
        self.clearAllCheckBox()
        for step in steps:
            if step['tipo_etapa_id'] == 3:
                continue
            self.buildCheckBox(
                f"{step['lote']} - {step['subfase']} - {step['etapa']} {step['ordem']}",
                step
            )

    def getSapStepsByFeatureId(self, featureIdList):
        subphaseIdSet = set()
        for featureId in featureIdList:
            featid = self.qgis.getActiveLayerAttribute(featureId, 'subfase_id')
            subphaseIdSet.add(featid)
            if len(subphaseIdSet) > 1:
                break

        if len(subphaseIdSet) > 1:
            raise Exception("Verificar unidades de trabalho selecionadas para que a seleção contenha apenas uma subfase")
        featureId = featureIdList[0]
        subphaseId = self.qgis.getActiveLayerAttribute(featureId, 'subfase_id')
        loteId = self.qgis.getActiveLayerAttribute(featureId, 'lote_id')
        steps = self.sap.getSteps()
        return [ 
            step for step in steps 
            if step['subfase_id'] == subphaseId and step['lote_id'] == loteId
        ]

    def buildCheckBox(self, text, dump):
        userCkb = QtWidgets.QCheckBox(text, self.scrollAreaWidgetContents)
        userCkb.dump = dump
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

    def getStepIds(self):
        checkeds = []
        checkboxs = self.getAllCheckBox()
        for checkbox in checkboxs:
            if not checkbox.isChecked():
               continue
            checkeds.append(checkbox)
        
        hasRevision = filter(lambda item: item.dump['tipo_etapa_id'] == 2, checkeds)
        corrections = []
        if hasRevision:
            whiteListOrder = [ r.dump['ordem'] + 1 for r in hasRevision]
            corrections = list(filter(lambda item: item.dump['ordem'] in whiteListOrder, checkboxs))
        return [int(c.dump['etapa_id']) for c in checkeds + corrections]
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('createActivities', 'activity')
        self.workspacesIdsLe.setText(values)
        self.loadSteps()
        