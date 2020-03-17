import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dialogs.inputDialog  import InputDialog

class AddFmeServerForm(InputDialog):

    def __init__(self, parent=None):
        super(AddFmeServerForm, self).__init__(parent)
        self.setValidatorIpv4(self.serverLe)
        self.setValidatorPort(self.portLe)

    def setValidatorPort(self, lineEdit):
        regex = QtCore.QRegExp("[0-9][0-9][0-9][0-9][0-9]")
        validator = QtGui.QRegExpValidator()
        validator.setRegExp(regex)
        lineEdit.setValidator(validator)

    def setValidatorIpv4(self, lineEdit):
        regex = QtCore.QRegExp("http://((1{0,1}[0-9]{0,2}|2[0-4]{1,1}[0-9]{1,1}|25[0-5]{1,1})\\.){3,3}(1{0,1}[0-9]{0,2}|2[0-4]{1,1}[0-9]{1,1}|25[0-5]{1,1})")
        validator = QtGui.QRegExpValidator()
        validator.setRegExp(regex)
        lineEdit.setValidator(validator)
        lineEdit.setText('http://')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addFmeServerForm.ui'
        )

    def clearInput(self):
        self.serverLe.setText('http://')
        self.portLe.setText('')
    
    def validInput(self):
        return (
            self.serverLe.text()
            and
            self.portLe.text()
        )

    def getData(self):
        return {
            'servidor': self.serverLe.text(),
            'porta': self.portLe.text()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()