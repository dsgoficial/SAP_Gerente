import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QComboBox, QTableWidgetItem

class SortLabelTableWidgetItem(QTableWidgetItem):

    def __init__(self):
        super(SortLabelTableWidgetItem, self).__init__()

    def __lt__(self, other):
        return self.getCurrentValue() < self.getOtherValue(other)

    def getCurrentValue(self):
        widget = self.tableWidget().cellWidget(self.row(), self.column()).layout().itemAt(0).widget()
        return widget.text()

    def getOtherValue(self, other):
        widget = self.tableWidget().cellWidget(other.row(), other.column()).layout().itemAt(0).widget()
        return widget.text()