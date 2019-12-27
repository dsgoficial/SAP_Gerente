import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.sap.views.dialogs.inputDialog  import InputDialog

class AddRuleForm(InputDialog):

    def __init__(self, widgetExpression, parent=None):
        super(AddRuleForm, self).__init__(parent)
        self.widgetExpression = widgetExpression
        self.expressionLayout.addWidget(self.widgetExpression)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis',
            'addRuleForm.ui'
        )
    
    def validInput(self):
        return (
            self.groupLe.text()
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

    def getData(self):
        return {
            'grupo_regra': self.groupLe.text(),
            'camada': self.layerLe.text(),
            'schema': self.schemaLe.text(),
            'atributo': self.attributeLe.text(),
            'descricao': self.descriptionTe.toPlainText(),
            'regra': self.widgetExpression.expression()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showMessageErro('Aviso', 'Preencha todos os campos!')
            return
        self.accept()

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.reject()
        

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.model3')
        self.pathFileLe.setText(filePath[0])
