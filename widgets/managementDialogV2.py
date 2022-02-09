import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory

class ManagementDialogV2(QtWidgets.QDialog):
    
    def __init__(self, 
            controller, 
            parent=None,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(ManagementDialogV2, self).__init__(parent=parent)
        uic.loadUi(self.getUiPath(), self)
        self.controller = controller
        self.messageFactory = messageFactory
        self.tableWidget.horizontalHeader().sortIndicatorOrder()
        self.tableWidget.setSortingEnabled(True)

    def hiddenColumns(self, columns):
        [ self.tableWidget.setColumnHidden(idx, True) for idx in columns ]

    def hiddenTableColumns(self, tableWidget, columns):
        [ tableWidget.setColumnHidden(idx, True) for idx in columns ]

    def getRowData(self):
        raise NotImplementedError()

    def getColumnsIndexToSearch(self):
        raise NotImplementedError()
    
    def getRowIndex(self, rowId):
        if not rowId:
            return -1
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    rowId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def createToolButton(self, tableWidget, tooltip, iconPath ):
        button = QtWidgets.QPushButton('', tableWidget)
        button.setToolTip( tooltip )
        button.setIcon(QtGui.QIcon( iconPath ))
        button.setFixedSize(QtCore.QSize(25, 25))
        button.setIconSize(QtCore.QSize(20, 20))
        return button

    def getEditIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'edit.png'
        )

    def getDeleteIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'trash.png'
        )

    def createRowEditWidget(self, 
            tableWidget, 
            row, 
            col, 
            editCallback, 
            deleteCallback
        ):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        index = QtCore.QPersistentModelIndex(tableWidget.model().index(row, col))

        editBtn = self.createToolButton( tableWidget, 'Editar', self.getEditIconPath() )
        editBtn.clicked.connect(
            lambda *args, index=index: editCallback(index)
        )
        layout.addWidget(editBtn)

        deleteBtn = self.createToolButton( tableWidget, 'Deletar', self.getDeleteIconPath() )
        deleteBtn.clicked.connect(
            lambda *args, index=index: deleteCallback(index)
        )
        layout.addWidget(deleteBtn)

        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

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

    def setController(self, controller):
        self.controller = controller

    def getController(self):
        return self.controller

    def clearAllTableItems(self, tableWidget):
        tableWidget.setRowCount(0)
    
    def adjustColumns(self):
        self.tableWidget.resizeColumnsToContents()

    def adjustRows(self):
        self.tableWidget.resizeRowsToContents()

    def adjustTable(self):
        self.adjustColumns()
        self.adjustRows()

    def removeSelected(self):
        while self.tableWidget.selectionModel().selectedRows() :
            self.tableWidget.removeRow(self.tableWidget.selectionModel().selectedRows()[0].row())

    def hasTextOnRow(self, rowIdx, text):
        for colIdx in self.getColumnsIndexToSearch():
            cellText = self.tableWidget.model().index(rowIdx, colIdx).data()
            if cellText and text.lower() in cellText.lower():
                return True
        return False

    def closeEvent(self, e):
        self.closeChildren(QtWidgets.QDialog)
        super().closeEvent(e)

    def closeChildren(self, typeWidget):
        [ d.close() for d in self.findChildren(typeWidget) ]
