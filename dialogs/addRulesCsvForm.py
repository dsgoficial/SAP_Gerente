import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dialogs.inputDialog  import InputDialog

class AddRulesCsvForm(InputDialog):

    def __init__(self, controller, parent=None):
        super(AddRulesCsvForm, self).__init__(parent)
        self.controller = controller
        self.templateBtn.setIcon(QtGui.QIcon(self.getDownloadIconPath()))
        self.selectCsvBtn.setIcon(QtGui.QIcon(self.getUploadIconPath()))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addRulesCsvForm.ui'
        )

    def getDownloadIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'download.png'
        )

    def getUploadIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'upload.png'
        )

    def clearInput(self):
        self.pathCsvLe.setText('')
    
    def validInput(self):
        return self.pathCsvLe.text()

    def getData(self):
        return {
            'pathRulesCsv': self.pathCsvLe.text()
        }
    
    @QtCore.pyqtSlot(bool)
    def on_templateBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getSaveFileName(
            self, 
            '',
            "REGRAS.csv",
            '*.csv'
        )
        if not filePath[0]:
            return
        self.controller.downloadCsvRulesTemplate(filePath[0])
        self.showInfo('Aviso', 'Modelo Baixado!')
    
    @QtCore.pyqtSlot(bool)
    def on_selectCsvBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            '',
            "Desktop",
            '*.csv'
        )
        if not filePath[0]:
            return
        self.pathCsvLe.setText(filePath[0])

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()