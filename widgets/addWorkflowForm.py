import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddWorkflowForm(InputDialog):

    save = QtCore.pyqtSignal()

    def __init__(self, sap, parent=None):
        super(AddWorkflowForm, self).__init__(parent=parent)
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addWorkflowForm.ui'
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
            'workflow_json' : self.getFileData()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos e selecione um arquivo de workflow!')
            return
        message = self.sap.createWorkflows([self.getData()])
        self.showInfo('Aviso', message)
        self.save.emit()
        self.accept()

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.workflow')
        self.pathFileLe.setText(filePath[0])
