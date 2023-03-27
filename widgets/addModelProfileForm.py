import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddModelProfileForm(InputDialog):

    def __init__(self, sap, parent=None):
        super(AddModelProfileForm, self).__init__(parent=parent)
        self.sap = sap
        self.orderLe.setValidator(QtGui.QIntValidator(0, 1000))
        self.loadModels(self.sap.getModels())
        self.loadLots(self.sap.getLots())
        self.loadRoutines(self.sap.getRoutines())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addModelProfileForm.ui'
        )

    def loadModels(self, models):
        self.modelsCb.clear()
        self.modelsCb.addItem('...', None)
        for model in models:
            self.modelsCb.addItem(model['nome'], model['id'])

    def loadRoutines(self, routines):
        self.routinesCb.clear()
        self.routinesCb.addItem('...', None)
        for routine in routines:
            self.routinesCb.addItem(routine['nome'], routine['code'])

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

    def clearInput(self):
        self.subphaseCb.setCurrentIndex(0)
        self.modelsCb.setCurrentIndex(0)
        self.routinesCb.setCurrentIndex(0)
        self.lotCb.setCurrentIndex(0)
        self.completionCkb.setChecked(False)
        self.orderLe.setText('')

    def validInput(self):
        return (
            self.subphaseCb.currentIndex() != 0
            and
            self.modelsCb.currentIndex() != 0
            and
            self.orderLe.text() != ''
        )

    def getData(self):
        return {
            'qgis_model_id': self.modelsCb.itemData(self.modelsCb.currentIndex()),  
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex()),
            'tipo_rotina_id': self.routinesCb.itemData(self.routinesCb.currentIndex()),
            'lote_id': self.lotCb.itemData(self.lotCb.currentIndex()),
            'requisito_finalizacao': self.completionCkb.isChecked(),
            'ordem': int(self.orderLe.text()),
            'parametros': self.parametersLe.text()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
    
        try:
            message = self.sap.createModelProfiles(
                [self.getData()]
            )
            self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))
