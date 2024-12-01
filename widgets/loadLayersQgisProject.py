import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
 
class LoadLayersQgisProject(DockWidget):

    def __init__(self, controller, sap):
        super(LoadLayersQgisProject, self).__init__(controller=controller)
        self.sap = sap
        self.setWindowTitle('Carregar Camadas de Acompanhamento')
        self.projectInProgressCkb.setChecked(True)
        self.lotInProgressCkb.setChecked(True)
        self.updateCheckboxes()

        self.loadCombo(
            self.blockCb, 
            [
                {'id': i, 'value': i['nome']} 
                for i in self.sap.getBlocks()
            ]
        )

    def updateCheckboxes(self):
        # Se projetos em andamento estiver desmarcado, desabilitar e desmarcar lotes
        if not self.projectInProgressCkb.isChecked():
            self.lotInProgressCkb.setEnabled(False)
            self.lotInProgressCkb.setChecked(False)
        else:
            self.lotInProgressCkb.setEnabled(True)

    @QtCore.pyqtSlot(int)
    def on_projectInProgressCkb_stateChanged(self, state):
        self.updateCheckboxes()

    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('Todos os blocos', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "loadLayersQgisProject.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return True

    def runFunction(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.controller.loadLayersQgisProject(
                self.projectInProgressCkb.isChecked(),
                self.blockCb.itemData(self.blockCb.currentIndex()),
                self.lotInProgressCkb.isChecked()
            )
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        self.close()