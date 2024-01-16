import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddProfileMonitoring(InputDialogV2):

    def __init__(
            self, 
            sap,
            parent=None
        ):
        super(AddProfileMonitoring, self).__init__(parent=parent)
        self.setWindowTitle('Adicionar Perfil Monitoramento')
        self.sap = sap
        self.loadCombo(
            self.lotCb, 
            [
                {'id': i['id'], 'value': i['nome']} 
                for i in self.sap.getLots()
            ]
        )
        self.loadCombo(
            self.profileCb, 
            [
                {'id': i['code'], 'value': i['nome']} 
                for i in self.sap.getMonitoringTypes()
            ]
        )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProfileMonitoring.ui'
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
            'tipo_monitoramento_id': self.profileCb.itemData(self.profileCb.currentIndex()),
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex()),
            'lote_id': self.lotCb.itemData(self.lotCb.currentIndex())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.profileCb.setCurrentIndex(self.profileCb.findData(data['tipo_monitoramento_id']))
        self.lotCb.setCurrentIndex(self.lotCb.findData(data['lote_id']))
        self.subphaseCb.setCurrentIndex(self.subphaseCb.findData(data['subfase_id']))

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        try:
            data = self.getData()
            if not (
                data['tipo_monitoramento_id'] and
                data['subfase_id'] and
                data['lote_id']
            ):
                self.showError('Aviso', 'Preencha todos os campos!')
                return
            
            if self.isEditMode():
                message = self.sap.updateWorkflowProfiles([self.getData()])
            else:
                message = self.sap.createMonitoringProfiles([self.getData()])
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))