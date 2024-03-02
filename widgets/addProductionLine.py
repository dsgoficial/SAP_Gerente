import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
import json
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddProductionLine(InputDialogV2):

    def __init__(self, controller, qgis, sap, parent=None):
        super(AddProductionLine, self).__init__(parent=parent)
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProductionLine.ui'
        )

    def validInput(self):
        return self.pathFileLe.text() and self.getFileData()

    def getFileData(self):
        filePath = self.pathFileLe.text()
        data = ''
        with open(filePath, 'r') as f:
            data = f.read()
        return json.loads(data)

    def getData(self):
        return {
            'linha_producao' : self.getFileData()
        }

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.json *.JSON')
        self.pathFileLe.setText(filePath[0])

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos e selecione um arquivo (.json) com a linha de produção!')
            return
        
        message = self.sap.createProductLine(self.getData())

        self.showInfo('Aviso', message)
        self.accept()

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.close()
    
