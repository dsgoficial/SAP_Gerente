import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddUserProfileProduction(InputDialogV2):

    def __init__(
            self, 
            sap,
            controller, 
            users,
            profiles,
            parent=None
        ):
        super(AddUserProfileProduction, self).__init__(
            controller=controller,
            parent=parent
        )
        self.setWindowTitle('Adicionar/Editar Perfil de Produção')
        self.loadUsers(users)
        self.loadProfiles(profiles)
        self.sap = sap

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

    def loadUsers(self, data):
        self.userCb.clear()
        self.userCb.addItem('...', None)
        for d in data:
            self.userCb.addItem('{} {}'.format(d['tipo_posto_grad'], d['nome']), d['id'])

    def getData(self):
        data = {
            'usuario_id': int(self.userCb.itemData(self.userCb.currentIndex())),
            'perfil_producao_id' : int(self.profileCb.itemData(self.profileCb.currentIndex()))
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.profileCb.setCurrentIndex(self.profileCb.findData(data['perfil_producao_id']))
        self.userCb.setCurrentIndex(self.userCb.findData(data['usuario_id']))

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        try:
            if self.isEditMode():
                message = self.sap.updateUserProfileProduction([self.getData()])
            else:
                message = self.sap.createUserProfileProduction([self.getData()])
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))

    def updateProfiles(self):
        self.loadProfiles(
            self.getController().getSapProductionProfiles()
        )
        #self.save.emit()