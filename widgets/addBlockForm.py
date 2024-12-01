import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddBlockForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddBlockForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Bloco')
        self.loadCombo(self.lotsCb, [{'id': i['id'], 'value': i['nome']} for i in self.sap.getLots()])
        self.loadCombo(
            self.statusCb, 
            [
                {'id': i['code'], 'value': i['nome']} 
                for i in self.sap.getStatusDomain()
            ]
        )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addBlockForm.ui'
        )

    def validInput(self):
        return (
            self.nameLe.text()
            and
            self.priorityLe.text()
            and
            self.lotsCb.itemData(self.lotsCb.currentIndex())
            and
            self.statusCb.itemData(self.statusCb.currentIndex())
        )

    def getData(self):
        data = {
            'nome': self.nameLe.text(),
            'prioridade': int(self.priorityLe.text()),
            'lote_id': self.lotsCb.itemData(self.lotsCb.currentIndex()),
            'status_id': self.statusCb.itemData(self.statusCb.currentIndex())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.nameLe.setText(data['nome'])
        self.priorityLe.setText(str(data['prioridade']))
        self.lotsCb.setCurrentIndex(self.lotsCb.findData(data['lote_id']))
        self.statusCb.setCurrentIndex(self.statusCb.findData(data['status_id']))
        
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
                message = self.sap.updateBlocks(
                    data
                )
            else:
                message = self.sap.createBlocks(
                    data
                )
            self.accept()
            message and self.showInfo('Aviso', message)
            self.save.emit()
        except Exception as e:
            self.showError('Erro', str(e))
        