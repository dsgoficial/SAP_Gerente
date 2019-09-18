# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui

class SapDocker(QtWidgets.QDockWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'sapDocker.ui'
    )

    icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        '..',
        'icons',
        '1cgeo.png'
    )

    def __init__(self, iface):
        super(SapDocker, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.tabWidget.setTabIcon(0, QtGui.QIcon(self.icon_path))
        self.tabWidget.setTabIcon(1, QtGui.QIcon(self.icon_path))
        self.tabWidget.setTabIcon(2, QtGui.QIcon(self.icon_path))