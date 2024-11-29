import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddMenuForm(InputDialogV2):

    def __init__(self, sap, parent=None):
        super(AddMenuForm, self).__init__(parent=parent)
        self.sap = sap
        self.selectedRgbColor = ''
        self.currentId = None
        self.currentMenu = None

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addMenuForm.ui'
        )

    def getFileData(self):
        filePath = self.pathFileLe.text()
        if not filePath:
            return self.currentMenu
        data = ''
        with open(filePath, 'r') as f:
            data = f.read()
        return data

    def validInput(self):
        return True

    def getData(self):
        data = {
            'nome' : self.nameLe.text(),
            'definicao_menu' : self.getFileData()
        }
        if self.currentId:
            data['id'] = self.currentId
        return data

    def setData(self, currentId, name, menu):
        self.currentId = currentId
        self.currentMenu = menu
        self.nameLe.setText(name)

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos e selecione um arquivo de menu!')
            return
        try:
            data = [self.getData()]
            if self.isEditMode():
                message = self.sap.updateMenus(
                    data
                )
            else:
                message = self.sap.createMenus(
                    data
                )
            self.accept()
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Erro', str(e))
        

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.json')
        self.pathFileLe.setText(filePath[0])

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.close()
