import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddUserBlock(InputDialogV2):

    def __init__(self, userId, controller, sap, parent):
        super(AddUserBlock, self).__init__(
            controller=controller,
            parent=parent
        )
        self.sap = sap
        self.setWindowTitle('Adicionar Bloco')
        self.setUserId(userId)
        self.loadBlocks(self.sap.getBlocks())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addUserBlock.ui'
        )
    
    def validInput(self):
        return self.projectCb.itemData(self.projectCb.currentIndex())

    def loadBlocks(self, data):
        self.projectCb.clear()
        self.projectCb.addItem('...', None)
        for d in data:
            self.projectCb.addItem(d['nome'], d['id'])

    def setUserId(self, userId):
        self.userId = userId

    def getUserId(self):
        return self.userId

    def getData(self):
        data = {
            'usuario_id': self.getUserId(),
            'bloco_id' : self.projectCb.itemData(
                self.projectCb.currentIndex()
            )
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.projectCb.setCurrentIndex(self.projectCb.findData(data['bloco_id']))

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        data = [self.getData()]
        if self.isEditMode():
            message = self.sap.updateUserBlockProduction(
                data
            )
        else:
            message = self.sap.createUserBlockProduction(
                data
            )
        self.accept()
        self.showError('Aviso', message)