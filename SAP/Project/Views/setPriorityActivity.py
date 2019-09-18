# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class SetPriorityActivity(QtWidgets.QWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'setPriorityActivity.ui'
    )

    run = QtCore.pyqtSignal()

    def __init__(self, iface, users):
        super(SetPriorityActivity, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.users = users
        self.users_cb.addItems(sorted([ user['nome'] for user in self.users]))
        self.ok_btn.clicked.connect( 
            self.validate_input    
        )

    def get_user_id(self):
        for user in self.users:
            if user['nome'] == self.users_cb.currentText():
                return user['id']

    def validate_input(self):
        if self.get_user_id() and self.activity_id_le.text() and self.priority_le.text():
            self.run.emit()
        else:
            html = "<p>Preencha todos os campos!</p>"
            msgBox.show(text=html, title=u"Erro", parent=self)

    def get_input_data(self):
        return {
            "param" : {
                "atividade_id" : int(self.activity_id_le.text()),
                "prioridade" : int(self.priority_le.text()),
                "usuario_prioridade_id" : self.get_user_id()
            },
            "function_name" : "set_priority_activity"
        }