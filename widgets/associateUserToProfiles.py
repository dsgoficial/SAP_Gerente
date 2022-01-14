import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AssociateUserToProfiles(InputDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(AssociateUserToProfiles, self).__init__(controller, parent)
        self.setWindowTitle('Associar Usuários para Perfis')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'associateUserToProfiles.ui'
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
    def on_addProfileBtn_clicked(self):
        self.getController().openAddProfileProduction(
            self,
            self.addRowProfileTable
        )

    def addRowProfileTable(self):
        pass