import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
 
class  DeleteFeatures(DockWidget):

    def __init__(self, sapCtrl):
        super(DeleteFeatures, self).__init__(controller=sapCtrl)
        self.loadIconBtn(
            self.removeByClipBtn, 
            self.getClipperIconPath(), 
            'Remove feições realizando um clip'
        )
        self.loadIconBtn(
            self.removeByIntersectBtn, 
            self.getIntersectIconPath(), 
            'Remove feições realizando uma interseção'
        )
        self.setWindowTitle('Remover Feições em Área')

    def loadIconBtn(self, button, pathIcon, toolTip):
        button.setIcon(QtGui.QIcon(pathIcon))
        button.setIconSize(QtCore.QSize(24,24))
        button.setToolTip(toolTip)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteFeatures.ui"
        )

    def getClipperIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons', 
            "clipper.png"
        )
    
    def getIntersectIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons', 
            "intersection.png"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    @QtCore.pyqtSlot(bool)
    def on_removeByClipBtn_clicked(self):
        self.controller.activeRemoveByClip()
    
    @QtCore.pyqtSlot(bool)
    def on_removeByIntersectBtn_clicked(self):
        self.controller.activeRemoveByIntersect()