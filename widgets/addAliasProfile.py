import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddAliasProfile(InputDialogV2):

    def __init__(
            self, 
            sap,
            parent=None
        ):
        super(AddAliasProfile, self).__init__()
        self.setWindowTitle('Adicionar Perfil Alias')
        self.sap = sap
        self.loadCombo(
            self.aliasCb, 
            [
                {'id': i['id'], 'value': i['nome']} 
                for i in self.sap.getAlias()
            ]
        )
        self.loadCombo(
            self.lotCb, 
            [
                {'id': i['id'], 'value': i['nome']} 
                for i in self.sap.getLots()
            ]
        )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addAliasProfile.ui'
        )

    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    @QtCore.pyqtSlot(int)
    def on_lotCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.subphaseCb.clear()
            return
        self.loadSubphases(self.lotCb.itemData(currentIndex))

    def loadSubphases(self, loteId):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        subphases = self.sap.getSubphases()
        subphases = [ s for s in subphases if s['lote_id'] == loteId ]
        subphases.sort(key=lambda item: int(item['subfase_id']), reverse=True) 
        for subphase in subphases:
            self.subphaseCb.addItem(
                "{} - {}".format(
                    subphase['fase'],
                    subphase['subfase']
                ), 
                subphase['subfase_id']
            )

    def getData(self):
        data = {
            'alias_id': self.aliasCb.itemData(self.aliasCb.currentIndex()),
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex()),
            'lote_id': self.lotCb.itemData(self.lotCb.currentIndex())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.aliasCb.setCurrentIndex(self.aliasCb.findData(data['alias_id']))
        self.lotCb.setCurrentIndex(self.lotCb.findData(data['lote_id']))
        self.subphaseCb.setCurrentIndex(self.subphaseCb.findData(data['subfase_id']))

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        try:
            data = self.getData()
            if not (
                data['alias_id'] and
                data['subfase_id'] and
                data['lote_id']
            ):
                self.showError('Aviso', 'Preencha todos os campos!')
                return
            
            if self.isEditMode():
                message = self.sap.updateAliasProfile([data])
            else:
                message = self.sap.createAliasProfile([data])
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))