# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class SelectFieldOptionQgis(QtWidgets.QDialog):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'uis', 
        'selectFieldOptionQgis.ui'
    )

    def __init__(self):
        super(SelectFieldOptionQgis, self).__init__()
        uic.loadUi(self.dialog_path, self)
        self.ok_btn.clicked.connect( 
            self.accept    
        )

    def chooseField(self, fieldsNames):
        self.fields_cb.addItems(sorted(fieldsNames))
        self.exec_()
        return self.fields_cb.currentText()