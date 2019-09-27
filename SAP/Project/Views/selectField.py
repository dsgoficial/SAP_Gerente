# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.utils import msgBox

class SelectField(QtWidgets.QDialog):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'selectField.ui'
    )

    def __init__(self, iface):
        super(SelectField, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.ok_btn.clicked.connect( 
            self.accept    
        )

    def get_field(self, fields_name):
        self.fields_cb.addItems(sorted(fields_name))
        self.exec_()
        return self.fields_cb.currentText()