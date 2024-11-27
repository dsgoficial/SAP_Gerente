import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddProjectForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddProjectForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Projeto')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProjectForm.ui'
        )

    def validInput(self):
        return (
            self.nameLe.text()
            and
            self.nameAbrevLe.text()
            and
            self.descriptionTe.toPlainText()
        )

    def getData(self):
        data = {
            'nome': self.nameLe.text(),
            'nome_abrev': self.nameAbrevLe.text(),
            'descricao': self.descriptionTe.toPlainText(),
            'status': self.finishedCkb.isChecked()
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.nameLe.setText(data['nome'])
        self.nameAbrevLe.setText(data['nome_abrev'])
        self.descriptionTe.setPlainText(data['descricao'])
        self.finishedCkb.setChecked(data['status'])

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        data = [self.getData()]
        if self.isEditMode():
            message = self.sap.updateProjects(
                data
            )
        else:
            message = self.sap.createProjects(
                data
            )
        self.accept()
        self.showInfo('Aviso', message)
        self.save.emit()