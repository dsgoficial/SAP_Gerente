import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2
import re

class AddPluginForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, sap, parent=None):
        super(AddPluginForm, self).__init__(parent=parent)
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addPluginForm.ui'
        )
    
    def validInput(self):
        if not self.nameLe.text():
            self.showError('Aviso', 'Preencha todos os campos!')
            return False
        if not  re.search('^\d+(\.\d+){0,2}$', self.versionLe.text()):
            self.showError('Aviso', 'Versão mínima incorreta!')
            return False
        return True

    def getData(self):
        data = {
            'nome' : self.nameLe.text(),
            'versao_minima' : self.versionLe.text()
        }
        if self.isEditMode():
            data['id'] = int(self.getCurrentId())
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.nameLe.setText(data['nome'])
        self.versionLe.setText(data['versao_minima'])

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        try:
            if not self.validInput():
                return
            data = self.getData()
            if self.isEditMode():
                message = self.sap.updatePlugins([data])
            else:
                message = self.sap.createPlugins([data])
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))
