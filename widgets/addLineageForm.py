import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddLineageForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddLineageForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Perfil Linhagem')
        self.loadShowTypes(self.sap.getShowTypes())
        self.loadLots(self.sap.getLots())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addLineageForm.ui'
        )

    def loadShowTypes(self, data):
        self.showTypeCb.clear()
        self.showTypeCb.addItem('...', None)
        for row in data:
            self.showTypeCb.addItem(row['nome'], row['code'])

    def loadLots(self, lots):
        self.lotCb.clear()
        self.lotCb.addItem('...', None)
        for lot in lots:
            self.lotCb.addItem(lot['nome'], lot['id'])

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

    def validInput(self):
        return (
            self.lotCb.itemData(self.lotCb.currentIndex())
            and
            self.subphaseCb.itemData(self.subphaseCb.currentIndex())
            and
            self.showTypeCb.itemData(self.showTypeCb.currentIndex())
        )

    def getData(self):
        data = {
            'lote_id': int(self.lotCb.itemData(self.lotCb.currentIndex())),
            'subfase_id': int(self.subphaseCb.itemData(self.subphaseCb.currentIndex())),
            'tipo_exibicao_id': int(self.showTypeCb.itemData(self.showTypeCb.currentIndex()))
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.lotCb.setCurrentIndex(self.lotCb.findData(data['lote_id']))
        self.subphaseCb.setCurrentIndex(self.subphaseCb.findData(data['subfase_id']))
        self.showTypeCb.setCurrentIndex(self.showTypeCb.findData(data['tipo_exibicao_id']))

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        data = [self.getData()]
        if self.isEditMode():
            message = self.sap.updateLineages(
                data
            )
        else:
            message = self.sap.createLineages(
                data
            )
        self.accept()
        message and self.showInfo('Aviso', message)
        self.save.emit()