import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class CreateProfileProduction(InputDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(CreateProfileProduction, self).__init__(controller, parent)
        self.setWindowTitle('Criar Perfil de Produção')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'createProfileProduction.ui'
        )

    def loadProfileProduction(self, data):
        self.userCb.clear()
        self.userCb.addItem('...', None)
        for d in data:
            self.userCb.addItem(
                '{} {}'.format(d['tipo_posto_grad'], d['nome']), 
                d['id']
            )

    def getData(self):
        return {
            'nome' : self.nameLe.text(),
            'descricao' : self.descriptionLe.toPlainText(),
            'model_xml' : self.getFileData()
        }

    @QtCore.pyqtSlot(bool)
    def on_addBtn_clicked(self):
        self.getController().openAddProfileProduction(
            self.updateTable
        )

    def updateTable(self):
        pass