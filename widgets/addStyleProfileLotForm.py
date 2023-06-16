import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddStyleProfileLotForm(InputDialog):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, qgis, sap, selected, parent=None):
        super(AddStyleProfileLotForm, self).__init__(parent=parent)
        self.sap = sap
        self.subphases = self.sap.getSubphases()
        self.selected = selected
        self.loadLots(self.sap.getLots())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addStyleProfileLotForm.ui'
        )

    def loadLots(self, lots):
        self.lotCb.clear()
        self.lotCb.addItem('...', None)
        for lot in lots:
            self.lotCb.addItem(lot['nome'], lot)

    def clearInput(self):
        self.lotCb.setCurrentIndex(0)

    def validInput(self):
        return self.lotCb.currentIndex() != 0

    """ def getData(self):
        data = []
        for s in self.selected:
            s['lote_id'] = self.lotCb.itemData(self.lotCb.currentIndex())
            data.append(s)
        return data """

    def getData(self):
        data = []
        lot = self.lotCb.itemData(self.lotCb.currentIndex())
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
            self.sap.createStyleProfiles(self.getData())
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showInfo('Aviso', 'Salvo com sucesso!')
            self.accept()
            self.save.emit()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Aviso', str(e))