import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2

class AssociateUserToProjects(MDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(AssociateUserToProjects, self).__init__(controller, parent)
        self.setWindowTitle('Associar Usuários para Projetos')
        self.userCb.currentIndexChanged.connect(self.updateWidgets)
        self.hiddenColumns([0, 1])

    def updateWidgets(self, index):
        self.clearAllTableItems(self.tableWidget)
        self.addProjectBtn.setEnabled(False)
        userId = self.getUserId()
        if userId is None:
            return
        self.addProjectBtn.setEnabled(True)
        self.updateProjectTable()

    def getUserId(self):
        return self.userCb.itemData(self.userCb.currentIndex())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'associateUserToProjects.ui'
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
        self.getController().openAddUserProject(
            self.getUserId(),
            self,
            self.updateProjectTable
        )

    def updateProjectTable(self):
        userId = self.getUserId()
        data = self.getController().getSapUserProject()
        self.addRows(filter(lambda d: d['usuario_id'] == userId, data))

    def getColumnsIndexToSearch(self):
        return []

    def handleEditBtn(self, index):
        self.getController().openEditUserProject(
            self.getUserId(),
            self.getRowData(index.row()),
            self,
            self.updateProjectTable
        )
        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        self.getController().deleteSapUserProject([data['id']], self)
        self.updateProjectTable()

    def addRow(self, 
            primaryKey, 
            projectId,
            project,
            priority
        ):
        idx = self.getRowIndex(str(primaryKey))
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(projectId))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(project))
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

    def addRows(self, data):
        self.clearAllTableItems(self.tableWidget)
        for d in data:  
            self.addRow(
                str(d['id']),
                d['projeto_id'],
                d['projeto'],
                d['prioridade']
            )
        self.adjustTable()

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'projeto_id': int(self.tableWidget.model().index(rowIndex, 1).data()),
            'prioridade': int(self.tableWidget.model().index(rowIndex, 3).data())
        }