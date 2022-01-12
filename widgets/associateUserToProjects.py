import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AssociateUserToProjects(InputDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(AssociateUserToProjects, self).__init__(controller, parent)
        self.setWindowTitle('Associar Usuários para Projetos')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'associateUserToProjects.ui'
        )

    def loadUsers(self, data):
        self.userCb.clear()
        self.userCb.addItem('...', None)
        for d in data:
            self.userCb.addItem(
                '{} {}'.format(d['tipo_posto_grad'], d['nome']), 
                d['id']
            )

    def getData(self):
        return {}

    @QtCore.pyqtSlot(bool)
    def on_addProjectBtn_clicked(self):
        self.getController().openAddProject(
            self,
            self.addRowProjectTable
        )

    def addRowProjectTable(self):
        pass

    @QtCore.pyqtSlot(bool)
    def on_connectBtn_clicked(self):
        pass

    def closeEvent(self, e):
        self.closeChildren(QtWidgets.QDialog)
        super().closeEvent(e)

    def closeChildren(self, typeWidget):
        [ d.close() for d in self.findChildren(typeWidget) ]