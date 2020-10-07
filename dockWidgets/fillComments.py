import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class FillComments(DockWidgetAutoComplete):

    def __init__(self, controller):
        super(FillComments, self).__init__(controller)
        self.loadIconBtn(self.refreshBtn, self.getRefreshIconPath(), 'Atualizar observações')
        self.loadIconBtn(self.getTemplateBtn, self.getExtractIconPath(), 'Extrair atividade id de modelo')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "fillComments.ui"
        )

    def getRefreshIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'icons', 
            "refresh.png"
        )

    def clearInput(self):
        self.activityIdLe.setText('')
        self.idTemplateLe.setText('')
        self.obsActivityLe.setText('')
        self.obsWorkspaceLe.setText('')
        self.obsStepLe.setText('')
        self.obsSubfaseLe.setText('')
        self.obsLotLe.setText('')

    def validInput(self):
        return  self.activityIdLe.text()

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.fillSapCommentActivity(
            self.getActivitiesIds(),
            self.obsActivityLe.text(),
            self.obsWorkspaceLe.text(),
            self.obsStepLe.text(),
            self.obsSubfaseLe.text(),
            self.obsLotLe.text()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('fillComments', 'activity')
        self.activityIdLe.setText(values)

    @QtCore.pyqtSlot(bool)
    def on_getTemplateBtn_clicked(self):
        values = self.controller.getValuesFromLayer('fillComments', 'activity')
        self.idTemplateLe.setText(values)

    @QtCore.pyqtSlot(bool)
    def on_refreshBtn_clicked(self):
        if self.idTemplateLe.text():
            comments = self.controller.getSapCommentsByActivity(
                self.idTemplateLe.text()
            )
            self.setComments(comments[0])

    def setComments(self, comments):
        self.obsActivityLe.setText(comments['observacao_etapa'])
        self.obsWorkspaceLe.setText(comments['observacao_subfase'])
        self.obsStepLe.setText(comments['observacao_lote'])
        self.obsSubfaseLe.setText(comments['observacao_unidade_trabalho'])
        self.obsLotLe.setText(comments['observacao_atividade'])
