import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class  LoadLayersQgisProject(DockWidget):

    def __init__(self, controller, sap):
        super(LoadLayersQgisProject, self).__init__(controller=controller)
        self.sap = sap
        self.setWindowTitle('Carregar Camadas de Acompanhamento')
        self.loadCombo(
            self.blockCb, 
            [
                {'id': i, 'value': i['nome']} 
                for i in self.sap.getBlocks()
            ]
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
        self.projectInProgressCkb.setChecked(False)

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
        