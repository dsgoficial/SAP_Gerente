# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class UnlockWorkspace(QtWidgets.QWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'unlockWorkspace.ui'
    )

    run = QtCore.pyqtSignal()

    def __init__(self, iface):
        super(UnlockWorkspace, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.ok_btn.clicked.connect( 
            self.validate_input    
        )

    def validate_input(self):
        if self.workspace_ids_le.text():
            self.run.emit()
        else:
            html = "<p>Preencha todos os campos!</p>"
            msgBox.show(text=html, title=u"Erro", parent=self)

    def get_input_data(self):
        return {
            "param" : {
                "unidade_trabalho_ids" : [ int(d) for d in self.workspace_ids_le.text().split(',')]
            },
            "function_name" : "unlock_workspace"
        }