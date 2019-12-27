import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

from Ferramentas_Gerencia.sap.views.dialogs.interfaces.IManagementDialog  import IManagementDialog

class ManagementDialog(QtWidgets.QDialog, IManagementDialog):
    
    def __init__(self, sapCtrl):
        super(ManagementDialog, self).__init__(sapCtrl=sapCtrl)
        uic.loadUi(self.getUiPath(), self)
        self.tableWidget.horizontalHeader().sortIndicatorOrder()
        self.tableWidget.setSortingEnabled(True)
        
    def getUiPath(self):
        raise NotImplementedError()

    def addRow(self):
        raise NotImplementedError()
    
    def getRowIndex(self):
        raise NotImplementedError()

    def getRowData(self):
        raise NotImplementedError()

    def getSelectedRowData(self):
        raise NotImplementedError()

    def getAllTableData(self):
        raise NotImplementedError()
    
    def hasTextOnRow(self):
        raise NotImplementedError()

    def importData(self):
        raise NotImplementedError()
    
    def saveData(self):
        raise NotImplementedError()

    def getColumnsIndexToSearch(self):
        raise NotImplementedError()

    def getSelectedRowData(self):
        rowsData = []
        for item in self.tableWidget.selectionModel().selectedRows():
            rowsData.append( self.getRowData(item.row()) )
        return rowsData

    def getAllTableData(self):
        rowsData = []
        for idx in range(self.tableWidget.rowCount()):
            rowsData.append( self.getRowData(idx) )
        return rowsData

    def show(self):
        super(QtWidgets.QDialog, self).show()
        self.raise_()
        self.activateWindow()

    def createNotEditableItem(self, value):
        item = QtWidgets.QTableWidgetItem(value)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        return item
    
    def createEditableItem(self, value):
        item = QtWidgets.QTableWidgetItem(value)
        return item

    def searchRows(self, text):
        for idx in range(self.tableWidget.rowCount()):
            if text and not self.hasTextOnRow(idx, text):
                self.tableWidget.setRowHidden(idx, True)
            else:
                self.tableWidget.setRowHidden(idx, False)                

    @QtCore.pyqtSlot(str)
    def on_searchLe_textEdited(self, text):
        self.searchRows(text)

    def showMessageErro(self, title, text):
        QtWidgets.QMessageBox.critical(
            self,
            title, 
            text
        )

    def showMessageInfo(self, title, text):
        QtWidgets.QMessageBox.information(
            self,
            title, 
            text
        )

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.openAddForm()
        QtWidgets.QApplication.restoreOverrideCursor()
    
    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.saveTable()
        QtWidgets.QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot(bool)
    def on_clearSelectionBtn_clicked(self):
        self.tableWidget.clearSelection()

    @QtCore.pyqtSlot(bool)
    def on_delBtn_clicked(self):
        while self.tableWidget.selectionModel().selectedRows():
            item = self.tableWidget.selectionModel().selectedRows()[0]
            self.tableWidget.removeRow(item.row())
            

    def hasTextOnRow(self, rowIdx, text):
        for colIdx in self.getColumnsIndexToSearch():
            cellText = self.tableWidget.model().index(rowIdx, colIdx).data()
            if cellText and text.lower() in cellText.lower():
                return True
        return False