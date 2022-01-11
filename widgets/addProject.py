import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddProject(InputDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(AddProject, self).__init__(parent)
        self.setWindowTitle('Adicionar Projeto')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProject.ui'
        )
    
    def validInput(self):
        return self.profileCb.itemData(self.profileCb.currentIndex()) and self.priorityLe.text()

    def loadProjects(self, data):
        self.profileCb.clear()
        self.profileCb.addItem('...', None)
        for d in data:
            self.profileCb.addItem(d['linha_producao'], d['linha_producao_id'])

    def getData(self):
        return {
            'name' : self.nameLe.text(),
            'priority' : self.descriptionLe.toPlainText()
        }

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        self.accept()
        self.save.emit(self.getData())