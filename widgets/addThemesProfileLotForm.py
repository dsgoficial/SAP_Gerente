import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddThemesProfileLotForm(InputDialog):

    def __init__(self, sap, selected, parent=None):
        super(AddThemesProfileLotForm, self).__init__(parent=parent)
        self.sap = sap
        self.selected = selected
        self.loadLots(self.sap.getLots())
        
    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addThemesProfileLotForm.ui'
        )

    def loadLots(self, lots):
        self.lotsCb.clear()
        self.lotsCb.addItem('...', None)
        selectedLotIds = [ s['lote_id'] for s in self.selected ]
        for lot in lots:
            """ if lot['id'] in selectedLotIds:
                continue """
            self.lotsCb.addItem(lot['nome'], lot['id'])

    def clearInput(self):
        self.lotsCb.setCurrentIndex(0)

    def validInput(self):
        return self.lotsCb.currentIndex() != 0

    def getData(self):
        data = []
        for s in self.selected:
            s['lote_id'] = int(self.lotsCb.itemData(self.lotsCb.currentIndex()))
            data.append(s)
        return data

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        try:
            self.sap.createThemesProfile(self.getData())
            self.showInfo('Aviso', 'Salvo com sucesso!')
        except Exception as e:
            self.showError('Aviso', str(e)) 
        self.accept()