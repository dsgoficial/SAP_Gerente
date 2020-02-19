import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class FillComments(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(FillComments, self).__init__(sapCtrl=sapCtrl)
        self.refreshBtn.setIcon(QtGui.QIcon(self.getRefreshIconPath()))
        self.refreshBtn.setIconSize(QtCore.QSize(24,24))
        self.refreshBtn.setToolTip('Atualizar observações')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "fillComments.ui"
        )

    def getRefreshIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons', 
            "refresh.png"
        )

    def clearInput(self):
        self.activityIdLe.setText('')
        self.idTemplateLe.setText('')
        self.obsActivityLe.setText(''),
        self.obsWorkspaceLe.setText(''),
        self.obsStepLe.setText(''),
        self.obsSubfaseLe.setText(''),
        self.obsLotLe.setText('')

    def validInput(self):
        return  self.activityIdLe.text()

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.fillCommentActivity(
            self.getActivitiesIds(),
            self.obsActivityLe.text(),
            self.obsWorkspaceLe.text(),
            self.obsStepLe.text(),
            self.obsSubfaseLe.text(),
            self.obsLotLe.text()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('fillComments', 'activity')
        self.activityIdLe.setText(values)

    @QtCore.pyqtSlot(bool)
    def on_refreshBtn_clicked(self):
        if self.idTemplateLe.text():
            comments = self.sapCtrl.getCommentsByActivity(
                self.idTemplateLe.text()
            )
            print(comments)
