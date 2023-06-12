import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class  SynchronizeUserInformation(DockWidget):

    def __init__(self, sapCtrl):
        super(SynchronizeUserInformation, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Sincronizar Informações de Usuários')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "synchronizeUserInformation.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def runFunction(self):
        self.controller.synchronizeSapUserInformation()