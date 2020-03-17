import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dialogs.inputDialog  import InputDialog

class AddRuleSetForm(InputDialog):

    def __init__(self, parent=None):
        super(AddRuleSetForm, self).__init__(parent)
        self.selectedRgbColor = ''
        self.currenGroups = []

    def setCurrentGroups(self, groupList):
        self.currenGroups = groupList

    def getCurrentGroups(self, groupList):
        return self.currenGroups

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addRuleSetForm.ui'
        )

    def clearInput(self):
        self.groupLe.setText('')
        self.colorBtn.setStyleSheet('')
        self.selectedRgbColor = ''
    
    def validInput(self):
        return (
            self.groupLe.text()
            and
            self.selectedRgbColor
        )

    def getData(self):
        return {
            'grupo_regra': self.groupLe.text(),
            'cor_rgb': self.selectedRgbColor
        }

    @QtCore.pyqtSlot(bool)
    def on_colorBtn_clicked(self):
        colorDlg = QtWidgets.QColorDialog()
        if self.selectedRgbColor:
            r, g, b = self.selectedRgbColor.split(',')
            colorDlg.setCurrentColor(QtGui.QColor(int(r), int(g), int(b)))
        if not colorDlg.exec():
            return
        r, g, b, _ = colorDlg.selectedColor().getRgb()
        self.selectedRgbColor = "{0},{1},{2}".format(r, g, b)
        self.colorBtn.setStyleSheet("QPushButton {background-color: rgb("+self.selectedRgbColor+")}")

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()