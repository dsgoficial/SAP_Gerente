import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialog  import InputDialog

class AddWorkflowProfileLotForm(InputDialog):

    def __init__(self, sap, selected, parent=None):
        super(AddWorkflowProfileLotForm, self).__init__(parent=parent)
        self.sap = sap
        self.selected = selected
        self.loadLots(self.sap.getLots())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addWorkflowProfileLotForm.ui'
        )

    def loadLots(self, lots):
        self.lotCb.clear()
        self.lotCb.addItem('...', None)
        for lot in lots:
            self.lotCb.addItem(lot['nome'], lot['id'])

    def clearInput(self):
        pass

    def validInput(self):
        return self.lotCb.currentIndex() != 0

    def getData(self):
        data = []
        for s in self.selected:
            # SAP 3.0: o validador recusa chave a mais (o `id` da linha copiada
            # e os nomes de exibição); o item leva só os campos de criação.
            s = {k: s[k] for k in ('workflow_dsgtools_id', 'requisito_finalizacao', 'subfase_id',) if k in s}
            s['lote_id'] = self.lotCb.itemData(self.lotCb.currentIndex())
            data.append(s)
        return data

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            self.sap.createWorkflowProfiles(self.getData())
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showInfo('Aviso', 'Salvo com sucesso!')
            self.accept()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Aviso', str(e))
