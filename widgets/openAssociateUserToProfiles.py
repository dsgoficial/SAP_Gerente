import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidgetV2  import DockWidgetV2
 
class  OpenAssociateUserToProfiles(DockWidgetV2):

    def __init__(self, sapCtrl, parent):
        super(OpenAssociateUserToProfiles, self).__init__(
            controller=sapCtrl,
            parent=parent
        )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "openManagement.ui"
        )

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.getController().openAssociateUserToProfiles(
                self
            )
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()