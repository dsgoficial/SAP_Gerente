import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddUserBlockLot(InputDialogV2):

    def __init__(self, blocks, controller, sap, parent):
        super(AddUserBlockLot, self).__init__(
            controller=controller,
            parent=parent
        )
        self.sap = sap
        self.blocks = blocks
        self.loadBlocks(self.blocks)
        self.loadUsers()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addUserBlockLot.ui'
        )

    def loadBlocks(self, data):
        self.blocksCb.clear()
        self.blocksCb.addItem('...', None)
        for d in data:
            self.blocksCb.addItem(d['nome'], d['id'])

    def loadUsers(self):
        self.clearAllCheckBox()
        for d in reversed(self.sap.getActiveUsers()):
            self.buildCheckBox(
                '{} {}'.format(d['tipo_posto_grad'], d['nome_guerra']), 
                str(d['id'])
            )

    def clearAllCheckBox(self):
        for checkbox in self.getAllCheckBox():
            checkbox.deleteLater()

    def getAllCheckBox(self):
        checkboxs = []
        for idx in range(self.verticalLayout.count()):
            widget = self.verticalLayout.itemAt(idx).widget()
            if not self.isCheckbox(widget):
                continue
            checkboxs.append(widget)
        return checkboxs

    def buildCheckBox(self, text, uuid):
        userCkb = QtWidgets.QCheckBox(text, self.scrollAreaWidgetContents)
        userCkb.setObjectName(uuid)
        self.verticalLayout.insertWidget(0, userCkb)

    def isCheckbox(self, widget):
        return type(widget) == QtWidgets.QCheckBox

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        data = self.getData()
        message = self.sap.createUserBlockProduction(
            data
        )
        self.accept()
        message and self.showInfo('Aviso', message)

    def validInput(self):
        return self.blocksCb.itemData(self.blocksCb.currentIndex()) and self.getUserIds()

    def getData(self):
        blockId = self.blocksCb.itemData(
            self.blocksCb.currentIndex()
        )
        return [
            {
                'usuario_id': userId,
                'bloco_id' : blockId
            }
            for userId in self.getUserIds()
        ]

    def getUserIds(self):
        stepsIds = []
        for checkbox in self.getAllCheckBox():
            if not checkbox.isChecked():
               continue
            stepsIds.append(int(checkbox.objectName()))
        return stepsIds