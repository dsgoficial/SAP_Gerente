import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
 
class  LoadLayersQgisProject(DockWidget):

    def __init__(self, controller, sap):
        super(LoadLayersQgisProject, self).__init__(controller=controller)
        self.sap = sap
        self.setWindowTitle('Carregar Camadas de Acompanhamento')
        self.projectInProgressCkb.setChecked(True)

    @QtCore.pyqtSlot(int)
    def on_projectInProgressCkb_stateChanged(self, state):
        inProgress = self.projectInProgressCkb.isChecked()
        if not inProgress:
            self.loadCombo(
                self.blockCb, 
                [
                    {'id': i, 'value': i['nome']} 
                    for i in self.sap.getBlocks()
                ]
            )
            return
        projects = self.sap.getAllProjects()
        lots = self.sap.getAllLots()
        blocks = self.sap.getAllBlocks()
        selectedBlocks = []
        for b in blocks:
            lote = next(filter(lambda item: b['lote_id'] == item['id'], lots), None)
            if not lote:
                continue
            project = next(filter(lambda item: lote['projeto_id'] == item['id'], projects), None)
            if not project:
                continue
            if project['status_id'] == 1:
                continue
            selectedBlocks.append({'id': b, 'value': b['nome']} )
        self.loadCombo(
            self.blockCb, 
            selectedBlocks
        )

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
        return  True

    def runFunction(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.controller.loadLayersQgisProject(
                self.projectInProgressCkb.isChecked(),
                self.blockCb.itemData(self.blockCb.currentIndex())
            )
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        self.close()
        