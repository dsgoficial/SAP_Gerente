import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2
import re

class AddShortcutForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, sap, parent=None):
        super(AddShortcutForm, self).__init__(parent=parent)
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addShortcutForm.ui'
        )
    
    def validInput(self):
        if not (self.toolLe.text() and self.shortcutLe.text()):
            self.showError('Aviso', 'Preencha todos os campos!')
            return False
        return True

    def getData(self):
        data = {
            'ferramenta' : self.toolLe.text(),
            'atalho' : self.shortcutLe.text(),
            'idioma': 'português' if self.languageCb.currentIndex() == 0 else 'inglês'
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.toolLe.setText(data['ferramenta'])
        self.shortcutLe.setText(data['atalho'])
        self.languageCb.setCurrentIndex(
            0 if data['idioma'] == 'português' else 1
        )

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        try:
            if not self.validInput():
                return
            data = self.getData()
            if self.isEditMode():
                message = self.sap.updateShortcuts([data])
            else:
                message = self.sap.createShortcuts([data])
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))
