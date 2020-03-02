# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class SelectFieldOption(QtWidgets.QDialog):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'uis', 
        'selectFieldOption.ui'
    )

    def __init__(self):
        super(SelectFieldOption, self).__init__()
        uic.loadUi(self.dialog_path, self)
        self.ok_btn.clicked.connect( 
            self.accept    
        )

    def chooseField(self, fieldsNames):
        self.fields_cb.clear()
        self.fields_cb.addItems(sorted(fieldsNames))
        if not self.exec_():
            return ''
        return self.fields_cb.currentText()