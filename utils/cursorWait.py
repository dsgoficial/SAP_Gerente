
from PyQt5 import QtCore, uic, QtWidgets

def start():
    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

def stop():
    QtWidgets.QApplication.restoreOverrideCursor()
