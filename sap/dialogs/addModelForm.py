import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.sap.dialogs.inputDialog  import InputDialog

class AddModelForm(InputDialog):

    def __init__(self, parent=None):
        super(AddModelForm, self).__init__(parent)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addModelForm.ui'
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
        return self.nameLe.text() and self.descriptionLe.toPlainText() and self.pathFileLe.text() and self.getFileData()

    def getData(self):
        return {
            'modelName' : self.nameLe.text(),
            'modelDescription' : self.descriptionLe.toPlainText(),
            'modelXml' : self.getFileData()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos e selecione um arquivo de modelo!')
            return
        self.accept()

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.reject()
        

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.model3')
        self.pathFileLe.setText(filePath[0])
