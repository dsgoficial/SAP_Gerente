# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.utils import msgBox

class CreatePriorityGroupActivity(QtWidgets.QWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'createPriorityGroupActivity.ui'
    )

    icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        '..',
        '..',
        'icons',
        'extract.png'
    )

    run = QtCore.pyqtSignal()

    extractValues = QtCore.pyqtSignal()

    def __init__(self, iface, profiles):
        super(CreatePriorityGroupActivity, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.extract_field_btn.setIcon(QtGui.QIcon(self.icon_path))
        self.extract_field_btn.setIconSize(QtCore.QSize(24,24))
        self.extract_field_btn.setToolTip('Extrair valores mediante seleções')
        self.profiles = profiles
        self.profiles_cb.addItems(sorted([ profile['nome'] for profile in self.profiles]))
        self.extract_field_btn.clicked.connect(
            self.extractValues.emit
        )
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

    def get_extraction_config(self):
        return [
            {
                "layer_name" : "subfase_",
                "field_name" : "atividade_id",
                "all_selection" : False,
                
            }
        ]