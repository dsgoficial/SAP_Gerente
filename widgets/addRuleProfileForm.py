import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddRuleProfileForm(InputDialog):

    def __init__(self, parent=None):
        super(AddRuleProfileForm, self).__init__(parent)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addRuleProfileForm.ui'
        )

    def loadSubphases(self, subphases):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        for subphase in subphases:
            self.subphaseCb.addItem(subphase['nome'], subphase['id'])

    def loadRuleGroups(self, ruleGroups):
        self.ruleGroupCb.clear()
        self.ruleGroupCb.addItem('...', None)
        for ruleGroup in ruleGroups:
            self.ruleGroupCb.addItem(ruleGroup['grupo_regra'], ruleGroup['id'])

    def clearInput(self):
        self.subphaseCb.setCurrentIndex(0)
        self.ruleGroupCb.setCurrentIndex(0)

    def validInput(self):
        return (
            self.subphaseCb.currentIndex() != 0
            and
            self.ruleGroupCb.currentIndex() != 0
        )

    def getData(self):
        return {
            'grupo_regra_id': int(self.ruleGroupCb.itemData(self.ruleGroupCb.currentIndex())),
            'subfase_id': int(self.subphaseCb.itemData(self.subphaseCb.currentIndex()))
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()