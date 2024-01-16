import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddUserBlock(InputDialogV2):

    def __init__(self, userId, blocks, controller, sap, parent):
        super(AddUserBlock, self).__init__(
            controller=controller,
            parent=parent
        )
        self.sap = sap
        self.setUserId(userId)
        self.blocks = blocks
        self.loadBlocks(self.blocks)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addUserBlock.ui'
        )
    
    def validInput(self):
        return self.blocksCb.itemData(self.blocksCb.currentIndex())

    def loadBlocks(self, data):
        self.blocksCb.clear()
        self.blocksCb.addItem('...', None)
        for d in data:
            self.blocksCb.addItem(d['nome'], d['id'])

    @QtCore.pyqtSlot(int)
    def on_blocksCb_currentIndexChanged(self, idx):
        blockId = self.blocksCb.itemData(idx)
        self.priorityLb.setText('')
        if not blockId:
            return
        block = next(filter(lambda item: item['id'] == blockId, self.blocks), None)    
        self.priorityLb.setText('<b>{}</b>'.format(str(block['prioridade'])))    

    def setUserId(self, userId):
        self.userId = userId

    def getUserId(self):
        return self.userId

    def getData(self):
        data = {
            'usuario_id': self.getUserId(),
            'bloco_id' : self.blocksCb.itemData(
                self.blocksCb.currentIndex()
            )
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.blocksCb.setCurrentIndex(self.blocksCb.findData(data['bloco_id']))

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
        self.showInfo('Aviso', message)