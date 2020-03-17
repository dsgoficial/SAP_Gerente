import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.sap.dialogs.inputDialog  import InputDialog

class AddRuleForm(InputDialog):

    def __init__(self, widgetExpression, parent=None):
        super(AddRuleForm, self).__init__(parent)
        self.widgetExpression = widgetExpression
        self.expressionLayout.addWidget(self.widgetExpression)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addRuleForm.ui'
        )

    def clearInput(self):
        self.layerLe.setText('')
        self.schemaLe.setText('')
        self.attributeLe.setText('')
        self.descriptionTe.setPlainText('')
        self.widgetExpression.setExpression('')
    
    def validInput(self):
        return (
            self.groupCb.currentText()
            and
            self.layerLe.text()
            and
            self.schemaLe.text()
            and
            self.attributeLe.text()
            and
            self.descriptionTe.toPlainText()
            and
            self.widgetExpression.expression()
        )

    def setGroupList(self, groupList):
        self.groupCb.clear()
        self.groupCb.addItems(groupList)

    def getData(self):
        return {
            'grupo_regra': self.groupCb.currentText(),
            'camada': self.layerLe.text(),
            'schema': self.schemaLe.text(),
            'atributo': self.attributeLe.text(),
            'descricao': self.descriptionTe.toPlainText(),
            'regra': self.widgetExpression.expression()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()
