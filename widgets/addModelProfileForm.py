import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddModelProfileForm(InputDialog):

    def __init__(self, parent=None):
        super(AddModelProfileForm, self).__init__(parent)
        self.orderLe.setValidator(QtGui.QIntValidator(0, 1000))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addModelProfileForm.ui'
        )

    def loadSubphases(self, subphases):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        for subphase in subphases:
            self.subphaseCb.addItem(subphase['nome'], subphase['id'])

    def loadModels(self, models):
        self.modelsCb.clear()
        self.modelsCb.addItem('...', None)
        for model in models:
            self.modelsCb.addItem(model['nome'], model['id'])

    def clearInput(self):
        self.subphaseCb.setCurrentIndex(0)
        self.modelsCb.setCurrentIndex(0)
        self.completionCkb.setChecked(False)
        self.falsePositiveCkb.setChecked(False)
        self.orderLe.setText('')

    def validInput(self):
        return (
            self.subphaseCb.currentIndex() != 0
            and
            self.modelsCb.currentIndex() != 0
            and
            self.orderLe.text() != 0
        )

    def getData(self):
        return {
            'qgis_model_id': self.modelsCb.itemData(self.modelsCb.currentIndex()),
            'subfase_id': self.subphaseCb.itemData(self.subphaseCb.currentIndex()),
            'requisito_finalizacao': self.completionCkb.isChecked(),
            'gera_falso_positivo': self.falsePositiveCkb.isChecked(),
            'ordem': int(self.orderLe.text())
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()