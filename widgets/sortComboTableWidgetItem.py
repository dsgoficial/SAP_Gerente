import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QComboBox, QTableWidgetItem

class SortComboTableWidgetItem(QTableWidgetItem):

    def __init__(self):
        super(SortComboTableWidgetItem, self).__init__()

    def __lt__(self, other):
        currentValue = self.getCurrentValue()
        otherValue = self.getOtherValue(other)
        if currentValue is None and otherValue is None:
            return False
        elif currentValue is None:
            return True
        elif otherValue is None:
            return False
        else:
            return currentValue < otherValue

    def getCurrentValue(self):
        cell = self.tableWidget().cellWidget(self.row(), self.column())
        if not cell:
            return None
        currentCombo = cell.layout().itemAt(0).widget()
        return currentCombo.currentText()

    def getOtherValue(self, other):
        cell = self.tableWidget().cellWidget(other.row(), other.column())
        if not cell:
            return None
        otherCombo = cell.layout().itemAt(0).widget()
        return otherCombo.currentText()