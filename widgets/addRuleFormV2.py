import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddRuleFormV2(InputDialogV2):

    def __init__(self, sap, parent=None):
        super(AddRuleFormV2, self).__init__(parent=parent)
        self.selectedRgbColor = ''
        self.currentId = None
        self.currentRule = None
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addRuleFormV2.ui'
        )

    def getFileData(self):
        filePath = self.pathFileLe.text()
        if not filePath:
            return self.currentRule
        data = ''
        with open(filePath, 'r') as f:
            data = f.read()
        return data

    def validInput(self):
        return True

    def getData(self):
        data = {
            'nome' : self.nameLe.text(),
            'regra' : self.getFileData(),
            # 'cor_rgb': self.selectedRgbColor,
            # 'atributo': self.attrLe.text(),
            # 'ordem': int(self.orderLe.text())
        }
        if self.currentId:
            data['id'] = self.currentId
        return data

    def setData(self, currentId, name, rule):
        self.currentId = currentId
        self.currentRule = rule
        self.nameLe.setText(name)

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
            self.showError('Aviso', 'Preencha todos os campos e selecione um arquivo de modelo!')
            return
        if self.currentId:
            message = self.sap.updateRules(
                [self.getData()]
            )
        else:
            message = self.sap.createRules(
                [self.getData()]
            )
        self.showInfo('Aviso', message)
        self.accept()

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.json')
        self.pathFileLe.setText(filePath[0])

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.close()
