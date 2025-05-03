import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialog  import InputDialog

class AddRuleProfileLotForm(InputDialog):

    def __init__(self, sap, selected, parent=None):
        super(AddRuleProfileLotForm, self).__init__(parent=parent)
        self.sap = sap
        self.subphases = self.sap.getSubphases()
        self.selected = selected
        self.loadLots(self.sap.getLots())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addRuleProfileLotForm.ui'
        )

    def loadLots(self, lots):
        self.lotsCb.clear()
        self.lotsCb.addItem('...', None)
        selected_lot_ids = set(item['lote_id'] for item in self.selected)
        for lot in lots:
            if int(lot['id']) not in selected_lot_ids:
                self.lotsCb.addItem(lot['nome'], lot)

    def clearInput(self):
        self.lotsCb.setCurrentIndex(0)

    def validInput(self):
        return self.lotsCb.currentIndex() != 0

    def getData(self):
        data = []
        lot = self.lotsCb.itemData(self.lotsCb.currentIndex())
        for s in self.selected:
            subphase = next(filter(lambda item: item['subfase_id'] == s['subfase_id'], self.subphases), None)
            if subphase['linha_producao_id'] != lot['linha_producao_id']:
                raise Exception('Não é permitido copiar para linhas de produção diferentes!')
            s['lote_id'] = int(lot['id'])
            data.append(s)
        return data

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.sap.createRuleProfiles(self.getData())
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showInfo('Aviso', 'Salvo com sucesso!')
            self.accept()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Aviso', str(e))