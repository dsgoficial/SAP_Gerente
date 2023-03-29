import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddProductionDataForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddProductionDataForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Dado Produção')
        self.loadCombo(self.typeProductionDataCb, [{'id': i['code'], 'value': i['nome']} for i in self.sap.getProductionDataType()])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProductionDataForm.ui'
        )

    def validInput(self):
        return (
            self.productionSetupLe.text()
            and
            self.typeProductionDataCb.itemData(self.typeProductionDataCb.currentIndex())
        )

    def getData(self):
        data = {
            'configuracao_producao': self.productionSetupLe.text(),
            'tipo_dado_producao_id': self.typeProductionDataCb.itemData(self.typeProductionDataCb.currentIndex())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.productionSetupLe.setText(data['configuracao_producao'])
        self.typeProductionDataCb.setCurrentIndex(self.typeProductionDataCb.findData(data['tipo_dado_producao_id']))
        
    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        try:
            data = [self.getData()]
            if self.isEditMode():
                message = self.sap.updateProductionData(
                    data
                )
            else:
                message = self.sap.createProductionData(
                    data
                )
            self.accept()
            self.showInfo('Aviso', message)
            self.save.emit()
        except Exception as e:
            self.showError('Erro', str(e))
        