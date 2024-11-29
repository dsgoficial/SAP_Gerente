import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialog  import InputDialog

class AddMenuProfileForm(InputDialog):

    def __init__(self, sap, parent=None):
        super(AddMenuProfileForm, self).__init__(parent=parent)
        self.sap = sap
        self.loadMenus(self.sap.getMenus())
        self.loadLots(self.sap.getLots())
        
    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addMenuProfileForm.ui'
        )

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

    def loadMenus(self, menus):
        self.menusCb.clear()
        self.menusCb.addItem('...', None)
        for menu in menus:
            self.menusCb.addItem(menu['nome'], menu['id'])

    def clearInput(self):
        self.subphaseCb.setCurrentIndex(0)
        self.lotCb.setCurrentIndex(0)
        self.menusCb.setCurrentIndex(0)

    def validInput(self):
        return (
            self.subphaseCb.currentIndex() != 0
            and
            self.lotCb.currentIndex() != 0
            and
            self.menusCb.currentIndex() != 0
        )

    def getData(self):
        return {
            'menu_id': int(self.menusCb.itemData(self.menusCb.currentIndex())),
            'subfase_id': int(self.subphaseCb.itemData(self.subphaseCb.currentIndex())),
            'lote_id': int(self.lotCb.itemData(self.lotCb.currentIndex())),
            'menu_revisao': self.revCkb.isChecked()
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        try:
            message = self.sap.createMenuProfiles([self.getData()])
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e)) 
        self.accept()