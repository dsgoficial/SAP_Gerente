import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class  UpdateLayersQgisProject(DockWidget):

    def __init__(self, controller, sap):
        super(UpdateLayersQgisProject, self).__init__(controller=controller)
        self.sap = sap
        self.setWindowTitle('Atualizar Camadas de Acompanhamento')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "updateLayersQgisProject.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def runFunction(self):
        self.sap.updateLayersQgisProject()
        self.showInfo('Atualizado com sucesso!')