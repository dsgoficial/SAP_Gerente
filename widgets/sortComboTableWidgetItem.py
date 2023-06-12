import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QComboBox, QTableWidgetItem

class SortComboTableWidgetItem(QTableWidgetItem):

    def __init__(self):
        super(SortComboTableWidgetItem, self).__init__()

    def __lt__(self, other):
        return self.getCurrentValue() < self.getOtherValue(other)

    def getCurrentValue(self):
        if not self.tableWidget().cellWidget(self.row(), self.column()):
            return None
        currentCombo = self.tableWidget().cellWidget(self.row(), self.column()).layout().itemAt(0).widget()
        return currentCombo.currentText()

    def getOtherValue(self, other):
        otherCombo = self.tableWidget().cellWidget(other.row(), other.column()).layout().itemAt(0).widget()
        return otherCombo.currentText()