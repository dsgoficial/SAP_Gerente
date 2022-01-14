import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2
from Ferramentas_Gerencia.widgets.managementDialogV2  import ManagementDialogV2

class ProductionProfileEditor(ManagementDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, parent=None):
        super(ProductionProfileEditor, self).__init__(controller, parent)
        self.setWindowTitle('Editar Perfis')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'productionProfileEditor.ui'
        )

    def loadProfiles(self, data):
        self.addRows(data)

    @QtCore.pyqtSlot(bool)
    def on_closeBtn_clicked(self):
        self.close()

    @QtCore.pyqtSlot(bool)
    def on_createProfileBtn_clicked(self):
        self.getController().openCreateProfileProduction(
            self,
            self.updateProfiles
        )

    def updateProfiles(self):
        self.loadProfiles(
            self.getController().getSapProductionProfiles()
        )
        self.save.emit()

    def getColumnsIndexToSearch(self):
        return [1]

    def handleEditBtn(self, index):
        data = self.getRowData(index.row())
        self.getController().openEditProfileProduction(
            data,
            self,
            self.updateProfiles
        )
        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        self.getController().deleteSapProductionProfiles([data['id']], self)
        self.showInfo('Aviso', "Perfil deletado!")
        self.updateProfiles()

    def addRow(self, 
            primaryKey, 
            name
        ):
        idx = self.getRowIndex(str(primaryKey))
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        self.tableWidget.setItem(idx, 1, self.createNotEditableItem(name))
        self.tableWidget.setCellWidget(
            idx, 
            2, 
            self.createRowEditWidget(
                self.tableWidget,
                idx, 
                2, 
                self.handleEditBtn, 
                self.handleDeleteBtn
            )
        )

    def addRows(self, data):
        self.clearAllItems()
        for d in data:  
            self.addRow(
                str(d['id']), 
                d['nome']
            )
        self.adjustTable()

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'nome': self.tableWidget.model().index(rowIndex, 1).data()
        }