import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2
from .testDatabase  import TestDatabase

class AddProductionDataForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddProductionDataForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Banco de Dados de Produção')
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
            self.ipDBLe.text()
            and
            self.portDBLe.text()
            and
            self.nameDBLe.text()
            and
            self.typeProductionDataCb.itemData(self.typeProductionDataCb.currentIndex())            
        )

    def getData(self):
        data = {
            'configuracao_producao': "{}:{}/{}".format(
                self.ipDBLe.text(),
                self.portDBLe.text(),
                self.nameDBLe.text()
            ),
            'tipo_dado_producao_id': self.typeProductionDataCb.itemData(self.typeProductionDataCb.currentIndex())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.ipDBLe.setText(data['configuracao_producao'].split('/')[0].split(':')[0])
        self.portDBLe.setText(data['configuracao_producao'].split('/')[0].split(':')[1])
        self.nameDBLe.setText(data['configuracao_producao'].split('/')[-1])
        self.typeProductionDataCb.setCurrentIndex(self.typeProductionDataCb.findData(data['tipo_dado_producao_id']))
        
    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    def hasDatabase(self):
        result = TestDatabase(
            self.ipDBLe.text(),
            self.portDBLe.text(),
            self.nameDBLe.text(),
            self
        ).exec_()
        return QtWidgets.QDialog.Accepted == result

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        if not self.hasDatabase():
            self.showError('Aviso', 'Sem conexão com o banco!')
            return
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            data = [self.getData()]
            if self.isEditMode():
                message = self.sap.updateProductionData(
                    data
                )
            else:
                message = self.sap.createProductionData(
                    data
                )
            QtWidgets.QApplication.restoreOverrideCursor()
            self.accept()
            self.showInfo('Aviso', message)
            self.save.emit()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Erro', str(e))            
        