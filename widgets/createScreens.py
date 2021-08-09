import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class  CreateScreens(DockWidget):

    def __init__(self, sapCtrl):
        super(CreateScreens, self).__init__(controller=sapCtrl)
        self.loadIconBtn(self.layerPrimaryBtn, self.getExtractIconPath(), 'Carregar camadas selecionadas')
        self.loadIconBtn(self.layerSecundaryBtn, self.getExtractIconPath(), 'Carregar camadas selecionadas')

    def getExtractIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'extract.png'
        )

    def loadIconBtn(self, button, pathIcon, toolTip):
        button.setIcon(QtGui.QIcon(pathIcon))
        button.setIconSize(QtCore.QSize(24,24))
        button.setToolTip(toolTip)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createScreens.ui"
        )

    @QtCore.pyqtSlot(bool)
    def on_layerPrimaryBtn_clicked(self):
        self.layerPrimaryLe.setText( 
            self.controller.getScreenLayers( 'createScreens', 'primary' ) 
        )
    
    @QtCore.pyqtSlot(bool)
    def on_layerSecundaryBtn_clicked(self):
        self.layerSecundaryLe.setText( 
            self.controller.getScreenLayers( 'createScreens', 'secundary' ) 
        )

    def clearInput(self):
        self.layerPrimaryLe.setText('')
        self.layerSecundaryLe.setText('')

    def validInput(self):
        return  self.layerPrimaryLe.text() and self.layerSecundaryLe.text()

    def runFunction(self):
        primaryLayerNames = self.layerPrimaryLe.text().split(',')
        secundaryLayerNames = self.layerSecundaryLe.text().split(',')
        self.controller.createScreens( primaryLayerNames, secundaryLayerNames)

        