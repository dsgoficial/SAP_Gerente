# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.utils import msgBox

class OpenActivity(QtWidgets.QWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'openActivity.ui'
    )

    run = QtCore.pyqtSignal()

    def __init__(self, iface):
        super(OpenActivity, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.ok_btn.clicked.connect( 
            self.validate_input    
        )

    def validate_input(self):
        if self.activity_id.text():
            self.run.emit()
        else:
            html = "<p>Preencha todos os campos!</p>"
            msgBox.show(text=html, title=u"Erro", parent=self)

    def get_input_data(self):
        return {
            "param" : {
                "atividade_id" : self.activity_id.text()
            },
            "function_name" : "open_activity"
        }
