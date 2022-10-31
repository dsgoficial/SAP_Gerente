import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory

class MDialog(QtWidgets.QDialog):
    
    def __init__(self, 
            controller, 
            parent=None,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(MDialog, self).__init__(parent=parent)
        uic.loadUi(self.getUiPath(), self)
        self.controller = controller
        self.messageFactory = messageFactory
        self.tableWidget.horizontalHeader().sortIndicatorOrder()
        self.tableWidget.setSortingEnabled(True)

    def getEditIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons', 
            "edit.png"
        )

    def getTrashIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons', 
            "trash.png"
        )

    def getDownloadIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons', 
            "download.png"
        )
        
    def getController(self):
        return self.controller 
        
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

    def createTableToolButton(self, tooltip, iconPath ):
        button = QtWidgets.QPushButton('', self.tableWidget)
        button.setToolTip( tooltip )
        button.setIcon(QtGui.QIcon( iconPath ))
        button.setFixedSize(QtCore.QSize(30, 30))
        button.setIconSize(QtCore.QSize(20, 20))
        return button

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

    """ def show(self):
        super(QtWidgets.QDialog, self).show()
        self.toTopLevel() """

    def toTopLevel(self):
        self.raise_()
        self.activateWindow()

    def validateValue(self, value):
        if value is None:
            return ''
        return str(value)

    def createNotEditableItem(self, value):
        item = QtWidgets.QTableWidgetItem(self.validateValue(value))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        return item
    
    def createEditableItem(self, value):
        item = QtWidgets.QTableWidgetItem(self.validateValue(value))
        return item

    def searchRows(self, text):
        for idx in range(self.tableWidget.rowCount()):
            if text and not self.hasTextOnRow(idx, text):
                self.tableWidget.setRowHidden(idx, True)
            else:
                self.tableWidget.setRowHidden(idx, False)                

    def showError(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showInfo(self, title, message):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)

    def clearAllItems(self):
        self.tableWidget.setRowCount(0)
    
    def adjustColumns(self):
        self.tableWidget.resizeColumnsToContents()

    def adjustRows(self):
        self.tableWidget.resizeRowsToContents()

    def removeSelected(self):
        while self.tableWidget.selectionModel().selectedRows() :
            self.tableWidget.removeRow(self.tableWidget.selectionModel().selectedRows()[0].row())

    def hasTextOnRow(self, rowIdx, text):
        for colIdx in self.getColumnsIndexToSearch():
            cellText = self.tableWidget.model().index(rowIdx, colIdx).data()
            if cellText and text.lower() in cellText.lower():
                return True
        return False

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.openAddForm()
    
    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.saveTable()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot(bool)
    def on_clearSelectionBtn_clicked(self):
        self.tableWidget.clearSelection()

    @QtCore.pyqtSlot(bool)
    def on_delBtn_clicked(self):
        self.removeSelected()
    
    @QtCore.pyqtSlot(str)
    def on_searchLe_textEdited(self, text):
        self.searchRows(text)
