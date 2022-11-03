import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddMenuProfileForm(InputDialog):

    def __init__(self, parent=None):
        super(AddMenuProfileForm, self).__init__(parent)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addMenuProfileForm.ui'
        )

    def loadSubphases(self, subphases):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        for subphase in subphases:
            self.subphaseCb.addItem(subphase['subfase'], subphase['subfase_id'])

    def loadMenus(self, menus):
        self.menusCb.clear()
        self.menusCb.addItem('...', None)
        for menu in menus:
            self.menusCb.addItem(menu['nome'], menu['id'])

    def loadLots(self, lots):
        self.lotsCb.clear()
        self.lotsCb.addItem('...', None)
        for lot in lots:
            self.lotsCb.addItem(lot['nome'], lot['id'])

    def clearInput(self):
        self.subphaseCb.setCurrentIndex(0)
        self.lotsCb.setCurrentIndex(0)
        self.menusCb.setCurrentIndex(0)

    def validInput(self):
        return (
            self.subphaseCb.currentIndex() != 0
            and
            self.lotsCb.currentIndex() != 0
            and
            self.menusCb.currentIndex() != 0
        )

    def getData(self):
        return {
            'menu_id': int(self.menusCb.itemData(self.menusCb.currentIndex())),
            'subfase_id': int(self.subphaseCb.itemData(self.subphaseCb.currentIndex())),
            'lote_id': int(self.lotsCb.itemData(self.lotsCb.currentIndex())),
            'menu_revisao': self.revCkb.isChecked()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()