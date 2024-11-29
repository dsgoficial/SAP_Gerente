import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddProfileDifficulty(InputDialogV2):

    def __init__(
            self, 
            sap,
            parent=None
        ):
        super(AddProfileDifficulty, self).__init__(parent=parent)
        self.setWindowTitle('Adicionar Perfil Dificuldade')
        self.sap = sap
        self.loadCombo(
            self.userCb, 
            [
                
                {'id': i['id'], 'value':  "{} - {}".format(
                    i['tipo_posto_grad'],
                    i['nome_guerra']
                )} 
                for i in self.sap.getActiveUsers()
            ]
        )
        self.loadCombo(
            self.profileCb, 
            [
                {'id': i['code'], 'value': i['tipo_perfil_dificuldade']} 
                for i in self.sap.getProfileDifficultyType()
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
            'addProfileDifficulty.ui'
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
        subphases = self.sap.getSubphases()
        subphases = [ s for s in subphases if s['lote_id'] == loteId ]
        subphases.sort(key=lambda item: int(item['subfase_id']), reverse=True) 
        self.loadCombo(
            self.subphaseCb, 
            [
                {'id': i['subfase_id'], 'value':  "{} - {}".format(
                    i['fase'],
                    i['subfase']
                )} 
                for i in subphases
            ]
        )

    def getData(self):
        data = {
            'usuario_id': self.userCb.itemData(self.userCb.currentIndex()),
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex()),
            'tipo_perfil_dificuldade_id': self.profileCb.itemData(self.profileCb.currentIndex()),
            'lote_id': self.lotCb.itemData(self.lotCb.currentIndex())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.userCb.setCurrentIndex(self.userCb.findData(data['usuario_id']))
        self.profileCb.setCurrentIndex(self.profileCb.findData(data['tipo_perfil_dificuldade_id']))
        self.lotCb.setCurrentIndex(self.lotCb.findData(data['lote_id']))
        self.subphaseCb.setCurrentIndex(self.subphaseCb.findData(data['subfase_id']))

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        try:
            data = self.getData()
            if not (
                data['usuario_id'] and
                data['subfase_id'] and
                data['tipo_perfil_dificuldade_id'] and
                data['lote_id']
            ):
                self.showError('Aviso', 'Preencha todos os campos!')
                return
            
            if self.isEditMode():
                message = self.sap.updateProfileDifficulty([self.getData()])
            else:
                message = self.sap.createProfileDifficulty([self.getData()])
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))