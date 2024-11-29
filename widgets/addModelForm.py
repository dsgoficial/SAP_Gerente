import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialog  import InputDialog

class AddModelForm(InputDialog):

    save = QtCore.pyqtSignal()

    def __init__(self, sap, parent=None):
        super(AddModelForm, self).__init__(parent=parent)
        self.sap = sap

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
            'nome' : self.nameLe.text(),
            'descricao' : self.descriptionLe.toPlainText(),
            'model_xml' : self.getFileData()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos e selecione um arquivo de modelo!')
            return
        message = self.sap.createModels([self.getData()])
        message and self.showInfo('Aviso', message)
        self.save.emit()
        self.accept()

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.model3')
        self.pathFileLe.setText(filePath[0])
