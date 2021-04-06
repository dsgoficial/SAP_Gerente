from PyQt5 import QtCore, uic, QtWidgets

class Message:

    def __init__(self):
        pass

    def showError(self, parent, title, text):
        QtWidgets.QMessageBox.critical(
            parent,
            title, 
            text
        )
    
    def showInfo(self, parent, title, text):
        QtWidgets.QMessageBox.information(
            parent,
            title, 
            text
        )