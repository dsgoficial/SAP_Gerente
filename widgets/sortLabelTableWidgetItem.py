import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QComboBox, QTableWidgetItem

class SortLabelTableWidgetItem(QTableWidgetItem):

    def __init__(self):
        super(SortLabelTableWidgetItem, self).__init__()

    def __lt__(self, other):
        return self.getCurrentValue() < self.getOtherValue(other)

    def getCurrentValue(self):
        cell = self.tableWidget().cellWidget(self.row(), self.column())
        if not(cell):
            return None
        widget = cell.layout().itemAt(0).widget()
        return widget.text()

    def getOtherValue(self, other):
        cell = self.tableWidget().cellWidget(other.row(), other.column())
        if not(cell):
            return None
        widget = cell.layout().itemAt(0).widget()
        return widget.text()