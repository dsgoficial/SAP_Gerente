import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class  DownloadQgisProject(DockWidget):

    def __init__(self, sapCtrl):
        super(DownloadQgisProject, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Gerar Projeto de Acompanhamento')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "downloadQgisProject.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def runFunction(self):
        filePath = QtWidgets.QFileDialog.getSaveFileName(
            self, 
            '',
            "PROJETO.qgs",
            '*.qgs'
        )
        if not filePath[0]:
            return
        self.controller.downloadSapQgisProject(filePath[0])