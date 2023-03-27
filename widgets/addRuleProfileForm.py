import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddRuleProfileForm(InputDialog):

    def __init__(self, sap, parent=None):
        super(AddRuleProfileForm, self).__init__(parent=parent)
        self.sap = sap
        self.loadRules(self.sap.getRules())
        self.loadLots(self.sap.getLots())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addRuleProfileForm.ui'
        )

    def loadRules(self, rules):
        self.rulesCb.clear()
        self.rulesCb.addItem('...', None)
        for rule in rules:
            self.rulesCb.addItem(rule['nome'], rule['id'])

    def loadLots(self, lots):
        self.lotsCb.clear()
        self.lotsCb.addItem('...', None)
        for lot in lots:
            self.lotsCb.addItem(lot['nome'], lot['id'])

    @QtCore.pyqtSlot(int)
    def on_lotsCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.subphaseCb.clear()
            return
        self.loadSubphases(self.lotsCb.itemData(currentIndex))

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
        self.subphaseCb.setCurrentIndex(0)
        self.lotsCb.setCurrentIndex(0)
        self.rulesCb.setCurrentIndex(0)

    def validInput(self):
        return (
            self.subphaseCb.currentIndex() != 0
            and
            self.lotsCb.currentIndex() != 0
            and
            self.rulesCb.currentIndex() != 0
        )

    def getData(self):
        return {
            'layer_rules_id': int(self.rulesCb.itemData(self.rulesCb.currentIndex())),
            'subfase_id': int(self.subphaseCb.itemData(self.subphaseCb.currentIndex())),
            'lote_id': int(self.lotsCb.itemData(self.lotsCb.currentIndex()))
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        message = self.sap.createRuleProfiles([self.getData()])
        self.showInfo('Aviso', message)
        self.accept()