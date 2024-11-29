import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class SetQgisVersion(InputDialogV2):

    def __init__(self, sap, parent=None):
        super(SetQgisVersion, self).__init__(parent=parent)
        self.sap = sap
        data = self.sap.getQgisVersion()
        self.qgisVersionLe.setText(data['versao_minima'])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'setQgisVersion.ui'
        )

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        version = {
            "versao_minima": self.qgisVersionLe.text()
        }
        if not self.qgisVersionLe.text():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        try:
            message = self.sap.updateQgisVersion(version)
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))
