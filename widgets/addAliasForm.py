import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddAliasForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, sap, parent=None):
        super(AddAliasForm, self).__init__(parent=parent)
        self.sap = sap
        self.currentAliasJSON = None

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addAliasForm.ui'
        )

    def getFileData(self):
        filePath = self.pathFileLe.text()
        data = ''
        with open(filePath, 'r') as f:
            data = f.read()
        return data

    def clearInput(self):
        pass
    
    def validInput(self):
        if self.isEditMode():
            return self.nameLe.text() and self.currentAliasJSON
        return self.nameLe.text() and self.pathFileLe.text() and self.getFileData()

    def getData(self):
        data = {
            'nome' : self.nameLe.text(),
            'definicao_alias' : self.getFileData()
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.nameLe.setText(data['nome'])
        self.currentAliasJSON = data['definicao_alias']

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        try:
            if not self.validInput():
                self.showError('Aviso', 'Preencha todos os campos e selecione um arquivo de modelo!')
                return
            data = self.getData()
            if self.isEditMode():
                message = self.sap.updateAlias([data])
            else:
                message = self.sap.createAlias([data])
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.json')
        self.pathFileLe.setText(filePath[0])
