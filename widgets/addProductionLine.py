import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
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
        linha = self.getData()['linha_producao']
        if isinstance(linha, dict) and 'tipo_produto_id' in linha:
            # SAP 3.0: o campo é `subtipo_produto_id` (os códigos são os mesmos do
            # tipo_produto do SAP 2.3.5), e o servidor recusa o nome antigo.
            self.showError('Aviso', 'O arquivo usa "tipo_produto_id". No SAP 3.0 o campo da linha de produção é "subtipo_produto_id" (mesmos códigos): renomeie no JSON.')
            return
        
        message = self.sap.createProductLine(self.getData())

        message and self.showInfo('Aviso', message)
        self.accept()

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.close()
    
