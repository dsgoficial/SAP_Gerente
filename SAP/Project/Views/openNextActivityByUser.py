# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class OpenNextActivityByUser(QtWidgets.QWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'openNextActivityByUser.ui'
    )

    run = QtCore.pyqtSignal()


    def __init__(self, iface, users):
        super(OpenNextActivityByUser, self).__init__()
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
        if self.get_user_id():
            self.run.emit()
        else:
            html = "<p>Preencha todos os campos!</p>"
            msgBox.show(text=html, title=u"Erro", parent=self)

    def get_input_data(self):
        return {
            "param" : {
                "user_id" : self.get_user_id()
            },
            "function_name" : "open_next_activity"
        }