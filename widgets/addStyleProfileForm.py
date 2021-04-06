import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddStyleProfileForm(InputDialog):

    def __init__(self, parent=None):
        super(AddStyleProfileForm, self).__init__(parent)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addStyleProfileForm.ui'
        )

    def loadSubphases(self, subphases):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        for subphase in subphases:
            self.subphaseCb.addItem(subphase['nome'], subphase['id'])

    def loadStyles(self, styles):
        self.stylesCb.clear()
        self.stylesCb.addItem('...', None)
        for style in styles:
            self.stylesCb.addItem(style['stylename'], style['stylename'])

    def clearInput(self):
        self.subphaseCb.setCurrentIndex(0)
        self.stylesCb.setCurrentIndex(0)

    def validInput(self):
        return (
            self.subphaseCb.currentIndex() != 0
            and
            self.stylesCb.currentIndex() != 0
        )

    def getData(self):
        return {
            'nome': self.stylesCb.itemData(self.stylesCb.currentIndex()),
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex())
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()