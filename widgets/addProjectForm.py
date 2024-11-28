import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddProjectForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddProjectForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Projeto')
        self.loadStatusCombo()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProjectForm.ui'
        )

    def loadStatusCombo(self):
        self.loadCombo(
            self.statusCb, 
            [
                {'id': i['code'], 'value': i['nome']} 
                for i in self.sap.getStatusDomain()
            ]
        )

    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    def validInput(self):
        return (
            self.nameLe.text()
            and
            self.nameAbrevLe.text()
            and
            self.descriptionTe.toPlainText()
            and
            self.statusCb.currentIndex() > 0  # Ensure a status is selected
        )

    def getData(self):
        data = {
            'nome': self.nameLe.text(),
            'nome_abrev': self.nameAbrevLe.text(),
            'descricao': self.descriptionTe.toPlainText(),
            'status_id': self.statusCb.currentData()  # Get the status ID
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.nameLe.setText(data['nome'])
        self.nameAbrevLe.setText(data['nome_abrev'])
        self.descriptionTe.setPlainText(data['descricao'])
        
        # Set the status in the combo box
        status_index = self.statusCb.findData(data['status_id'])
        if status_index >= 0:
            self.statusCb.setCurrentIndex(status_index)

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