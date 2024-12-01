# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from SAP_Gerente.config import Config

class Login(QtWidgets.QDialog):

    uiPath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'uis',
        'login.ui'
    )

    def __init__(self, loginCtrl):
        super(Login, self).__init__()
        uic.loadUi(self.uiPath, self)
        self.loginCtrl=loginCtrl
        self.version_text.setText("<b>versão: {}</b>".format(Config.VERSION))
        
    def loadData(self, user, password, server):
        self.userLe.setText(user) 
        self.serverLe.setText(server)  
        self.passwordLe.setText(password)

    def showView(self):
        return self.exec_()

    def closeView(self):
        self.close()

    def showErrorMessageBox(self, title, text):
        self.loginCtrl.showErrorMessageBox(
            self,
            title, 
            text
        )
        
    def validInput(self):
        test = ( 
            self.serverLe.text() 
            and  
            self.userLe.text() 
            and
            self.passwordLe.text()
        )
        return test

    @QtCore.pyqtSlot(bool)
    def on_submitBtn_clicked(self):
        if not self.validInput():
            html = u'<p style="color:red">Todos os campos devem ser preenchidos!</p>'
            self.showErrorMessageBox('Aviso', html)
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.login()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def login(self):
        user = self.userLe.text() 
        password = self.passwordLe.text()
        server = self.serverLe.text() 
        self.loginCtrl.authUser(user, password, server)

    
        


    