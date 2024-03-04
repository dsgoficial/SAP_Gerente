import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddPIT(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddPIT, self).__init__(parent=parent)
        self.sap = sap
        self.controller = controller
        self.setWindowTitle('Adicionar PIT')
        self.anoLe.setValidator( QtGui.QIntValidator(0, 100000) )
        self.metaLe.setValidator( QtGui.QIntValidator(0, 100000) )
        self.loadCombo(self.loteCb, [{'id': i['id'], 'value': i['nome']} for i in self.sap.getLots()])

    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])


    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addPIT.ui'
        )

    def validInput(self):
        data = self.getData()
        return (
            data['ano']
            and
            data['lote_id']
            and
            data['meta']
        )

    def getData(self):
        data = {
            'ano': int(self.anoLe.text()) if self.anoLe.text().isnumeric() else None,
            'lote_id': self.loteCb.itemData(self.loteCb.currentIndex()),
            'meta': int(self.metaLe.text()) if self.metaLe.text().isnumeric() else None
            
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.loteCb.setCurrentIndex(self.loteCb.findData(data['lote_id']))
        self.metaLe.setText(str(data['meta']))
        self.anoLe.setText(str(data['ano']))

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        data = [self.getData()]
        if self.isEditMode():
            message = self.sap.updatePITs(
                data
            )
        else:
            message = self.sap.createPITs(
                data
            )
        self.accept()
        self.showInfo('Aviso', message)
        self.save.emit()

    