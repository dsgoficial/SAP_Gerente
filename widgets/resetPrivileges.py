import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
 
class  ResetPrivileges(DockWidget):

    def __init__(self, sapCtrl):
        super(ResetPrivileges, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Redefinir Permissões')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "resetPrivileges.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def runFunction(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            result = self.controller.resetSapPrivileges()
            QtWidgets.QApplication.restoreOverrideCursor()
            if result:
                self.showInfo('Sucesso', result)
            else:
                self.showError('Erro', 'Não foi possível redefinir as permissões.')
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Erro', str(e))
        