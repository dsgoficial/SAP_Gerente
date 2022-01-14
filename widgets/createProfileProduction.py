import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class CreateProfileProduction(InputDialogV2):

    save = QtCore.pyqtSignal()

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

    def getData(self):
        data =  {
            'nome' : self.nameLe.text()
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.nameLe.setText(data['nome'])
        if self.isEditMode():
            self.setCurrentId(data['id'])

    def validInput(self):
        return self.getData()

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        data = self.getData()
        if self.isEditMode():
            self.getController().updateSapProductionProfiles(
                [ data ],
                self
            )
        else:
            self.getController().createSapProductionProfiles(
                [ data ],
                self
            )
        self.accept()
        self.save.emit()
