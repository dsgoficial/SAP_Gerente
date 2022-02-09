import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddUserProject(InputDialogV2):

    update = QtCore.pyqtSignal()

    def __init__(self, controller, parent=None):
        super(AddUserProject, self).__init__(
            controller=controller,
            parent=parent
        )
        self.setWindowTitle('Adicionar Projeto')
        self.priorityLe.setValidator(QtGui.QIntValidator(0, 1000))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addUserProject.ui'
        )
    
    def validInput(self):
        return self.projectCb.itemData(self.projectCb.currentIndex()) and self.priorityLe.text()

    def loadProjects(self, data):
        self.projectCb.clear()
        self.projectCb.addItem('...', None)
        for d in data:
            self.projectCb.addItem(d['nome'], d['id'])

    def setUserId(self, userId):
        self.userId = userId

    def getUserId(self):
        return self.userId

    def getData(self):
        data = {
            'usuario_id': self.getUserId(),
            'projeto_id' : self.projectCb.itemData(
                self.projectCb.currentIndex()
            ),
            'prioridade': int(self.priorityLe.text())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.projectCb.setCurrentIndex(self.projectCb.findData(data['projeto_id']))
        self.priorityLe.setText(str(data['prioridade']))

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        data = [self.getData()]
        if self.isEditMode():
            self.getController().updateSapUserProject(
                data,
                self
            )
        else:
            self.getController().createSapUserProject(
                data,
                self
            )
        self.accept()
        self.update.emit()