# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
import os

class LoginAction(QtWidgets.QAction):
    
    path_icon = os.path.join(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            "..", 
            ".."
        )),
        'icons',
        'icon.png'
    )

    show_login_dialog = QtCore.pyqtSignal()

    def __init__(self, iface): 
        super(LoginAction, self).__init__(
            QtGui.QIcon(self.path_icon),
            u"Ferramentas de Gerência",
            iface.mainWindow()
        )
        self.iface = iface 
        self.connect_signals()

    def connect_signals(self):
        self.triggered.connect(
            self.show_login_dialog.emit
        )

    def add_on_qgis(self):
        self.iface.digitizeToolBar().addAction(
            self
        )
    
    def remove_from_qgis(self):
        self.iface.digitizeToolBar().removeAction(
            self
        )