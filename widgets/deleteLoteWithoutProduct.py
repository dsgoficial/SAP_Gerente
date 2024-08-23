import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
 
class  DeleteLoteWithoutProduct(DockWidget):

    def __init__(self, sapCtrl):
        super(DeleteLoteWithoutProduct, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Deletar Lote sem Produto')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteLoteWithoutProduct.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def runFunction(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.controller.deleteSAPLoteWithoutProduct()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        