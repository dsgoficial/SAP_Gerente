import os, sys, copy
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
 
class  DeleteUTWithoutActivity(DockWidget):

    def __init__(self, sapCtrl):
        super(DeleteUTWithoutActivity, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Deletar Unidade de Trabalho sem Atividade')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteUTWithoutActivity.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def runFunction(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            self.controller.deleteSAPUTWithoutActivity()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        