# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class CreatePriorityGroupActivity(QtWidgets.QWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'createPriorityGroupActivity.ui'
    )

    run = QtCore.pyqtSignal()

    def __init__(self, iface, profiles):
        super(CreatePriorityGroupActivity, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.profiles = profiles
        self.profiles_cb.addItems(sorted([ profile['nome'] for profile in self.profiles]))
        self.ok_btn.clicked.connect( 
            self.validate_input    
        )

    def get_profile_id(self):
        for profile in self.profiles:
            if profile['nome'] == self.profiles_cb.currentText():
                return profile['id']

    def validate_input(self):
        if self.get_profile_id() and self.activity_id_le.text() and self.priority_le.text():
            self.run.emit()
        else:
            html = "<p>Preencha todos os campos!</p>"
            msgBox.show(text=html, title=u"Erro", parent=self)

    def get_input_data(self):
        return {
            "param" : {
                "atividade_id" : int(self.activity_id_le.text()),
                "prioridade" : int(self.priority_le.text()),
                "perfil_producao_id" : self.get_profile_id()
            },
            "function_name" : "create_priority_group_activity"
        }