import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddProfileProductionSetting(InputDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(AddProfileProductionSetting, self).__init__(
            controller=controller,
            parent=parent
        )
        self.sap = controller.sapCtrl
        self.setWindowTitle('Adicionar Configuração de Perfil de Produção')
        self.priorityLe.setValidator( QtGui.QIntValidator(0, 1000, self) )

        self.productionLineCb.currentIndexChanged.connect(self.on_productionLineCb_currentIndexChanged)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProfileProductionSetting.ui'
        )
    
    def loadProductionLines(self, data):
        self.productionLineCb.clear()
        self.productionLineCb.addItem('...', None)
        for d in data:
            self.productionLineCb.addItem(d['linha_producao'], d['linha_producao_id'])

    def validInput(self):
        return (
            self.productionLineCb.itemData(self.productionLineCb.currentIndex()) != None
            and
            self.subphaseCb.itemData(self.subphaseCb.currentIndex()) != None
            and
            self.stepCb.itemData(self.stepCb.currentIndex()) != None
            and
            self.priorityLe.text()
        )

    @QtCore.pyqtSlot(int)
    def on_productionLineCb_currentIndexChanged(self, index):
        production_line_id = self.productionLineCb.itemData(index)
        if production_line_id is None:
            self.subphaseCb.clear()
            self.subphaseCb.addItem('...', None)
            return
            
        # Filtrar subfases pela linha de produção selecionada
        subphases = self.sap.getSubphases()
        filtered_subphases = [d for d in subphases if d['linha_producao_id'] == production_line_id]
        self.loadSubphases(filtered_subphases)

    def loadSubphases(self, data):
        self.subphaseCb.clear()
        self.subphaseCb.addItem('...', None)
        loaded = []
        for d in data:
            itemId = d['subfase_id']
            if itemId in loaded:
                continue
            self.subphaseCb.addItem(
                "{} - {}".format(d['fase'], d['subfase']), 
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

        subphases = self.sap.getSubphases()
        subfase = next(filter(lambda item: item['subfase_id'] == data['subfase_id'], subphases), None)
        
        if subfase:
            # Definir a linha de produção primeiro
            production_line_index = self.productionLineCb.findData(subfase['linha_producao_id'])
            if production_line_index >= 0:
                self.productionLineCb.setCurrentIndex(production_line_index)

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