# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from qgis import utils

def show(text, title, status="information", parent=utils.iface.mainWindow()):
    if status == 'critical':
        m_box = QtWidgets.QMessageBox.critical
    elif status == 'question':
        m_box = QtWidgets.QMessageBox.question
    else:
        m_box = QtWidgets.QMessageBox.information
    result = m_box(
        parent,
        title,
        text
    )
    return result
