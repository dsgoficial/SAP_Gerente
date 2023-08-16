import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddWorkflowProfileForm(InputDialog):

    def __init__(self, sap, parent=None):
        super(AddWorkflowProfileForm, self).__init__(parent=parent)
        self.sap = sap
        self.loadWorkflow(self.sap.getWorkflows())
        self.loadLots(self.sap.getLots())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addWorkflowProfileForm.ui'
        )

    def loadWorkflow(self, models):
        self.workflowCb.clear()
        self.workflowCb.addItem('...', None)
        for model in models:
            self.workflowCb.addItem(model['nome'], model['id'])

    def loadLots(self, lots):
        self.lotCb.clear()
        self.lotCb.addItem('...', None)
        for lot in lots:
            self.lotCb.addItem(lot['nome'], lot['id'])

    @QtCore.pyqtSlot(int)
    def on_lotCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.subphaseCb.clear()
            return
        self.loadSubphases(self.lotCb.itemData(currentIndex))

    def loadSubphases(self, loteId):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        subphases = self.sap.getSubphases()
        subphases = [ s for s in subphases if s['lote_id'] == loteId ]
        subphases.sort(key=lambda item: int(item['subfase_id']), reverse=True) 
        for subphase in subphases:
            self.subphaseCb.addItem(
                "{} - {}".format(
                    subphase['fase'],
                    subphase['subfase']
                ), 
                subphase['subfase_id']
            )

    def clearInput(self):
        pass

    def validInput(self):
        return (
            self.subphaseCb.currentIndex() != 0
            and
            self.workflowCb.currentIndex() != 0
        )

    def getData(self):
        return {
            'workflow_dsgtools_id': self.workflowCb.itemData(self.workflowCb.currentIndex()),  
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex()),
            'lote_id': self.lotCb.itemData(self.lotCb.currentIndex()),
            'requisito_finalizacao': self.completionCkb.isChecked()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
    
        try:
            message = self.sap.createWorkflowProfiles(
                [self.getData()]
            )
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))
