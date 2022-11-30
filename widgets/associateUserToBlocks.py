import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2
from .addUserBlock import AddUserBlock

class AssociateUserToBlocks(MDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, qgis, sap, parent=None):
        super(AssociateUserToBlocks, self).__init__(controller, parent)
        self.sap = sap
        self.setWindowTitle('Associar Usuários para Blocos')
        self.userCb.currentIndexChanged.connect(self.updateWidgets)
        self.hiddenColumns([0, 1])
        self.setWindowTitle('Associar usuários à blocos')
        self.loadUsers( self.sap.getUsers() )
        self.addUserBlock = None
        self.fetchData()

    def updateWidgets(self, index):
        self.clearAllTableItems(self.tableWidget)
        self.addProjectBtn.setEnabled(False)
        userId = self.getUserId()
        if userId is None:
            return
        self.addProjectBtn.setEnabled(True)
        self.fetchData()

    def getUserId(self):
        return self.userCb.itemData(self.userCb.currentIndex())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'associateUserToBlocks.ui'
        )

    def loadUsers(self, data):
        self.userCb.clear()
        self.userCb.addItem('...', None)
        for d in data:
            self.userCb.addItem(
                '{} {}'.format(d['tipo_posto_grad'], d['nome']), 
                d['id']
            )

    def getData(self):
        return {}

    @QtCore.pyqtSlot(bool)
    def on_addProjectBtn_clicked(self):
        self.addUserBlock.close() if self.addUserBlock else None
        self.addUserBlock = AddUserBlock( self.getUserId(), self.getController(), self.sap, self)
        self.addUserBlock.accepted.connect(self.fetchData)
        self.addUserBlock.show()

    def fetchData(self):
        userId = self.getUserId()
        data = self.sap.getUserBlocks()
        blocks = self.sap.getBlocks()
        for d in data:
            block = next((p for p in blocks if p['id'] == d['bloco_id']), None)
            if not block:
                continue
            d['bloco'] = block['nome']
        self.addRows(filter(lambda d: d['usuario_id'] == userId, data))

    def getColumnsIndexToSearch(self):
        return []

    def handleEditBtn(self, index):
        self.addUserBlock.close() if self.addUserBlock else None
        self.addUserBlock = AddUserBlock( self.getUserId(), self.getController(), self.sap, self)
        self.addUserBlock.activeEditMode(True)
        data = self.getRowData(index.row())
        self.addUserBlock.setCurrentId(data['id'])
        self.addUserBlock.setData(data)
        self.addUserBlock.accepted.connect(self.fetchData)
        self.addUserBlock.show()
        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        self.sap.deleteUserBlockProduction([data['id']])
        self.fetchData()

    def addRow(self, 
            primaryKey, 
            blockId,
            block
        ):
        idx = self.getRowIndex(str(primaryKey))
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(blockId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(block))
        optionColumn = 3
        self.tableWidget.setCellWidget(
            idx, 
            optionColumn, 
            self.createRowEditWidget(
                self.tableWidget,
                idx, 
                optionColumn, 
                self.handleEditBtn, 
                self.handleDeleteBtn
            )
        )

    def addRows(self, data):
        self.clearAllTableItems(self.tableWidget)
        for d in data:  
            self.addRow(
                str(d['id']),
                d['bloco_id'],
                d['bloco']
            )
        self.adjustTable()

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'bloco_id': int(self.tableWidget.model().index(rowIndex, 1).data())
        }