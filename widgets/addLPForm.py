import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2 import InputDialogV2

class AddLPForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddLPForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Editar Disponibilidade')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addLPForm.ui'
        )

    def validInput(self):
        return True  # Always valid since we're just toggling a checkbox

    def getData(self):
        return {
            'id': self.getCurrentId(),
            'disponivel': self.disponivelCb.isChecked()
        }

    def setData(self, data):
        self.setCurrentId(data['linha_producao_id'])
        self.disponivelCb.setChecked(data['disponivel'])
        
    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        try:
            data = self.getData()
            message = self.sap.updateLinhaProducao([data])
            self.accept()
            message and self.showInfo('Aviso', message)
            self.save.emit()
        except Exception as e:
            self.showError('Erro', str(e))