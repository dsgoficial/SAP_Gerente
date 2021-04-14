import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

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
        self.attributeLe.setText('')
        self.descriptionTe.setPlainText('')
        self.widgetExpression.setExpression('')
    
    def validInput(self):
        return (
            self.groupCb.currentText()
            and
            self.layerCb.currentText()
            and
            self.attributeLe.text()
            and
            self.descriptionTe.toPlainText()
            and
            self.widgetExpression.expression()
        )

    def setGroupList(self, ruleSetData):
        self.groupCb.clear()
        for ruleSet in ruleSetData:
            self.groupCb.addItem(ruleSet['grupo_regra'], ruleSet['id'])

    def setLayerList(self, layers):
        self.layerCb.clear()
        layersSorted = sorted(layers, key=lambda k: k['nome']) 
        for layer in layersSorted:
            self.layerCb.addItem('{}.{}'.format(layer['schema'], layer['nome']), layer)

    def getData(self):
        return {
            'grupo_regra_id': self.groupCb.itemData(self.groupCb.currentIndex()),
            'schema': self.layerCb.itemData(self.layerCb.currentIndex())['schema'],
            'camada': self.layerCb.itemData(self.layerCb.currentIndex())['nome'],
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
