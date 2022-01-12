import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddProfileProductionSetting(InputDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(AddProfileProductionSetting, self).__init__(
            controller=controller,
            parent=parent
        )
        self.setWindowTitle('Adicionar Configuração Perfil de Producao')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProfileProductionSetting.ui'
        )
    
    def validInput(self):
        return self.profileCb.itemData(self.profileCb.currentIndex()) and self.priorityLe.text()

    def loadSubphases(self, data):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        for d in data:
            self.subphaseCb.addItem(d['nome'], d['id'])

    def loadSteps(self, data):
        self.stepCb.clear()
        self.stepCb.addItem('...', None)
        for d in data:
            self.stepCb.addItem(d['nome'], d['id'])

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
        pass

    def closeEvent(self, e):
        self.closeChildren(QtWidgets.QDialog)
        super().closeEvent(e)

    def closeChildren(self, typeWidget):
        [ d.close() for d in self.findChildren(typeWidget) ]