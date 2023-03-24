import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddLotForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddLotForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Lote')
        self.loadCombo(self.productionLinesCb, [{'id': i['linha_producao_id'], 'value': i['linha_producao']} for i in self.sap.getProductionLines()])
        self.loadCombo(self.projectsCb, [{'id': i['id'], 'value': i['nome']} for i in self.sap.getProjects()])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addLotForm.ui'
        )

    def validInput(self):
        return (
            self.nameLe.text()
            and
            self.nameAbrevLe.text()
            and
            self.descriptionTe.toPlainText()
            and
            self.projectsCb.itemData(self.projectsCb.currentIndex())
            and
            self.productionLinesCb.itemData(self.productionLinesCb.currentIndex())
        )

    def getData(self):
        data = {
            'nome': self.nameLe.text(),
            'nome_abrev': self.nameAbrevLe.text(),
            'descricao': self.descriptionTe.toPlainText(),
            'denominador_escala': int(self.scaleLe.text()),
            'projeto_id': self.projectsCb.itemData(self.projectsCb.currentIndex()),
            'linha_producao_id': self.productionLinesCb.itemData(self.productionLinesCb.currentIndex())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.nameLe.setText(data['nome'])
        self.nameAbrevLe.setText(data['nome_abrev'])
        self.descriptionTe.setPlainText(data['descricao'])
        self.scaleLe.setText(str(data['denominador_escala']))
        self.projectsCb.setCurrentIndex(self.projectsCb.findData(data['projeto_id']))
        self.productionLinesCb.setCurrentIndex(self.productionLinesCb.findData(data['linha_producao_id']))
        
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
        data = [self.getData()]
        if self.isEditMode():
            message = self.sap.updateLots(
                data
            )
        else:
            message = self.sap.createLots(
                data
            )
        self.accept()
        self.showInfo('Aviso', message)
        self.save.emit()