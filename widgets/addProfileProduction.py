import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddProfileProduction(InputDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(AddProfileProduction, self).__init__(
            controller=controller,
            parent=parent
        )
        self.setWindowTitle('Adicionar Perfil Produção')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProfileProduction.ui'
        )
    
    def validInput(self):
        return self.profileCb.itemData(self.profileCb.currentIndex()) and self.priorityLe.text()

    def loadProfiles(self, data):
        self.profileCb.clear()
        self.profileCb.addItem('...', None)
        for d in data:
            self.profileCb.addItem(d['nome'], d['id'])

    def getData(self):
        return {
            'nome' : self.nameLe.text(),
            'descricao' : self.descriptionLe.toPlainText(),
            'model_xml' : self.getFileData()
        }

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()
        self.save.emit(self.getData())

    @QtCore.pyqtSlot(bool)
    def on_userProfileMangerBtn_clicked(self):
        self.getController().openProductionProfileRelation(
            self,
            self.updateProfiles
        )

    def updateProfiles(self):
        pass