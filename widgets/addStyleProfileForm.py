import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialog  import InputDialog

class AddStyleProfileForm(InputDialog):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, qgis, sap, parent=None):
        super(AddStyleProfileForm, self).__init__(parent=parent)
        self.sap = sap
        self.loadSubphases(self.sap.getSubphases())
        self.loadGroupStyles(self.sap.getGroupStyles())
        self.loadLots(self.sap.getLots())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addStyleProfileForm.ui'
        )

    def loadGroupStyles(self, styles):
        self.stylesCb.clear()
        self.stylesCb.addItem('...', None)
        for style in styles:
            self.stylesCb.addItem(style['nome'], style['id'])

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
        self.stylesCb.setCurrentIndex(0)
        self.lotCb.setCurrentIndex(0)

    def validInput(self):
        return (
            self.subphaseCb.currentIndex() != 0
            and
            self.stylesCb.currentIndex() != 0
        )

    def getData(self):
        return {
            'grupo_estilo_id': self.stylesCb.itemData(self.stylesCb.currentIndex()),
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex()),
            'lote_id': self.lotCb.itemData(self.lotCb.currentIndex())
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        message = self.sap.createStyleProfiles([self.getData()])
        self.accept()
        self.save.emit()
        message and self.showInfo('Aviso', message)