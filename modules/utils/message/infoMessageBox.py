import os
from PyQt5 import QtWidgets, uic
from SAP_Gerente.modules.utils.interfaces.IMessage  import IMessage

class InfoMessageBox(IMessage):

    def __init__(self):
        super(InfoMessageBox, self).__init__()

    def show(self, parent, title, text):
        QtWidgets.QMessageBox.information(
            parent,
            title, 
            text
        )