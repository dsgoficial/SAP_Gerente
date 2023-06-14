import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2
import psycopg2

class TestDatabase(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, ip, port, dbname, parent=None):
        super(TestDatabase, self).__init__(parent=parent)
        self.ip = ip
        self.port = port
        self.dbname = dbname
        self.setWindowTitle('Validar Banco de Dados')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'testDatabase.ui'
        )

    def validInput(self):
        return (
            self.nameLe.text()
            and
            self.passLe.text()    
        )

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        try:
            conn = psycopg2.connect("dbname='{}' user='{}' password='{}' host='{}' port='{}'".format(
                self.dbname,
                self.nameLe.text(),
                self.passLe.text(),
                self.ip, 
                self.port
            ))
            conn.close()
            return self.accept()
        except Exception as e:
            return self.reject()              
        