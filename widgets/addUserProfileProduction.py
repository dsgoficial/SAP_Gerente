import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddUserProfileProduction(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, parent=None):
        super(AddUserProfileProduction, self).__init__(
            controller=controller,
            parent=parent
        )
        self.setWindowTitle('Adicionar Perfil Produção')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addUserProfileProduction.ui'
        )

    def validInput(self):
        return self.profileCb.itemData(self.profileCb.currentIndex())

    def loadProfiles(self, data):
        self.profileCb.clear()
        self.profileCb.addItem('...', None)
        for d in data:
            self.profileCb.addItem(d['nome'], d['id'])

    def getData(self):
        data = {
            'usuario_id': self.getUserId(),
            'perfil_producao_id' : int(self.profileCb.itemData(self.profileCb.currentIndex()))
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.profileCb.setCurrentIndex(self.profileCb.findData(data['perfil_producao_id']))

    def setUserId(self, userId):
        self.userId = userId

    def getUserId(self):
        return self.userId

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        if self.isEditMode():
            self.getController().updateSapUserProfileProduction([self.getData()], self)
        else:
            self.getController().createSapUserProfileProduction([self.getData()], self)
        self.save.emit()
        self.accept()

    @QtCore.pyqtSlot(bool)
    def on_userProfileMangerBtn_clicked(self):
        self.getController().openProductionProfileRelation(
            self,
            self.updateProfiles
        )

    def updateProfiles(self):
        self.loadProfiles(
            self.getController().getSapProductionProfiles()
        )
        self.save.emit()