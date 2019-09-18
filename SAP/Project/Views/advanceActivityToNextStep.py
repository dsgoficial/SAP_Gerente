# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class AdvanceActivityToNextStep(QtWidgets.QWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'advanceActivityToNextStep.ui'
    )

    run = QtCore.pyqtSignal()
    
    def __init__(self, iface):
        super(AdvanceActivityToNextStep, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.ok_btn.clicked.connect( 
            self.validate_input    
        )

    def validate_input(self):
        if self.activity_id_le.text() and self.finish_flag_ckb.isChecked():
            self.run.emit()
        else:
            html = "<p>Preencha todos os campos!</p>"
            msgBox.show(text=html, title=u"Erro", parent=self)

    def get_input_data(self):
        return {
            "param" : {
                "atividade_id" : int(self.activity_id_le.text()),
                "concluida" : self.finish_flag_ckb.isChecked()
            },
            "function_name" : "advance_activity_to_previous_step"
        }