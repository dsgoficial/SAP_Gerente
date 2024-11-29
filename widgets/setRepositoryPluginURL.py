import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class SetRepositoryPluginURL(InputDialogV2):

    def __init__(self, sap, parent=None):
        super(SetRepositoryPluginURL, self).__init__(parent=parent)
        self.sap = sap
        data = self.sap.getRemotePluginsPath()
        self.pluginPathLe.setText(data['dados']['path'])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'setRepositoryPluginURL.ui'
        )

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        if not self.pluginPathLe.text():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        try:
            message = self.sap.updateRemotePluginsPath(self.pluginPathLe.text())
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))
