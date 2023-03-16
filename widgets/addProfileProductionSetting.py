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
        self.priorityLe.setValidator( QtGui.QIntValidator(0, 1000, self) )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProfileProductionSetting.ui'
        )
    
    def validInput(self):
        return (
            self.subphaseCb.itemData( self.subphaseCb.currentIndex() ) != None
            and
            self.stepCb.itemData( self.stepCb.currentIndex() ) != None
            and
            self.priorityLe.text()
        )

    def loadSubphases(self, data):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        loaded = []
        for d in data:
            itemId = d['subfase_id']
            if itemId in loaded:
                continue
            self.subphaseCb.addItem(
                "{} - {} - {}".format(d['linha_producao'], d['fase'], d['subfase']), 
                itemId
            )
            loaded.append(itemId)

    def loadSteps(self, data):
        self.stepCb.clear()
        self.stepCb.addItem('...', None)
        for d in data:
            self.stepCb.addItem(d['nome'], d['code'])

    def getData(self):
        data =  {
            'subfase_id' : self.subphaseCb.itemData( self.subphaseCb.currentIndex() ),
            'tipo_etapa_id' : self.stepCb.itemData( self.stepCb.currentIndex() ),
            'prioridade' : int(self.priorityLe.text())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.subphaseCb.setCurrentIndex(self.subphaseCb.findData(data['subfase_id']))
        self.stepCb.setCurrentIndex(self.stepCb.findData(data['tipo_etapa_id']))
        self.priorityLe.setText(str(data['prioridade']))

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