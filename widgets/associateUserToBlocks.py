import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2
from .addUserBlock import AddUserBlock
from .addUserBlockLot import AddUserBlockLot

class AssociateUserToBlocks(MDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, qgis, sap, parent=None):
        super(AssociateUserToBlocks, self).__init__(controller, parent)
        self.sap = sap
        self.userCb.currentIndexChanged.connect(self.updateWidgets)
        self.hiddenColumns([0, 1])
        self.setWindowTitle('Associar Usuários à Blocos')
        self.loadUsers( self.sap.getActiveUsers() )
        self.addUserBlock = None
        self.addUserBlockLot = None
        self.fetchData()

    def updateWidgets(self, index):
        self.clearAllTableItems(self.tableWidget)
        self.addBtn.setEnabled(False)
        userId = self.getUserId()
        if userId is None:
            return
        self.addBtn.setEnabled(True)
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
                '{} {}'.format(d['tipo_posto_grad'], d['nome_guerra']), 
                d['id']
            )

    def getData(self):
        return {}

    @QtCore.pyqtSlot(bool)
    def on_addBtn_clicked(self):
        data = self.sap.getUserBlocks()
        userId = self.getUserId()
        currentBlockIds = [ d['bloco_id'] for d in data if d['usuario_id'] == userId]
        blocks = self.sap.getBlocks()
        self.addUserBlock.close() if self.addUserBlock else None
        self.addUserBlock = AddUserBlock( 
            self.getUserId(), 
            list(filter(lambda d: not(d['id'] in currentBlockIds), blocks)),
            self.getController(), 
            self.sap, 
            self
        )
        self.addUserBlock.setWindowTitle('Adicionar Bloco')
        self.addUserBlock.accepted.connect(self.fetchData)
        self.addUserBlock.show()

    @QtCore.pyqtSlot(bool)
    def on_addMultiBtn_clicked(self):
        self.addUserBlockLot.close() if self.addUserBlockLot else None
        self.addUserBlockLot = AddUserBlockLot( 
            self.sap.getBlocks(),
            self.getController(), 
            self.sap, 
            self
        )
        self.addUserBlockLot.setWindowTitle('Associar Usuários')
        self.addUserBlockLot.accepted.connect(self.fetchData)
        self.addUserBlockLot.show()

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
        data = self.sap.getUserBlocks()
        rowData = self.getRowData(index.row())
        currentBlockIds = [ d['bloco_id'] for d in data if rowData['bloco_id'] != d['bloco_id'] ]
        blocks = self.sap.getBlocks()
        self.addUserBlock.close() if self.addUserBlock else None
        self.addUserBlock = AddUserBlock( 
            self.getUserId(), 
            list(filter(lambda d: not(d['id'] in currentBlockIds), blocks)),
            self.getController(), 
            self.sap, 
            self
        )
        self.addUserBlock.setWindowTitle('Editar Bloco')
        self.addUserBlock.activeEditMode(True)
        data = self.getRowData(index.row())
        self.addUserBlock.setCurrentId(data['id'])
        self.addUserBlock.setData(data)
        self.addUserBlock.accepted.connect(self.fetchData)
        self.addUserBlock.show()
        
    def handleDeleteBtn(self, index):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir associação?')
        if not result:
            return
        data = self.getRowData(index.row())
        self.sap.deleteUserBlockProduction([data['id']])
        self.fetchData()

    def addRows(self, data):
        self.clearAllTableItems(self.tableWidget)
        for d in data:  
            self.addRow(
                str(d['id']),
                d['bloco_id'],
                d['bloco'],
                d['prioridade']
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            blockId,
            block,
            priority
        ):
        idx = self.getRowIndex(str(primaryKey))
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(blockId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(block))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(priority))
        optionColumn = 4
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

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'bloco_id': int(self.tableWidget.model().index(rowIndex, 1).data())
        }