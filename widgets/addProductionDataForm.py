import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2
from .testDatabase  import TestDatabase
import re

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
    
    def checkDatabaseName(self):
        nameDB = self.nameDBLe.text()
        regex = re.compile('[\.@!#$%^&*()<>?/\|}{~:]')
        if  (
                nameDB[0].isdigit()
                or
                len([l for l in nameDB if l.isupper()]) > 0
                or
                regex.search(nameDB)
            ):
            return False
        return True

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        if not self.checkDatabaseName():
            self.showError('Aviso', 'Nome do banco inválido!')
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
            message and self.showInfo('Aviso', message)
            self.save.emit()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Erro', str(e))            
        