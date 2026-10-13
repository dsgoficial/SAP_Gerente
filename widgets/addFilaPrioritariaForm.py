import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddFilaPrioritariaForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddFilaPrioritariaForm, self).__init__(parent=parent)
        self.sap = sap
        self.controller = controller
        self.setWindowTitle('Adicionar Fila Prioritária')
        self.prioridadeLe.setValidator( QtGui.QIntValidator(0, 100000) )
        self.loadCombo(self.projetoCb, [{'id': i['id'], 'value': i['nome']} for i in self.sap.getProjects()])
        self.loadCombo(self.usuarioCb, [{'id': i['uuid'], 'value': i['rotulo']} for i in self.sap.getActiveUsers()])

    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])


    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addFilaPrioritariaForm.ui'
        )

    def validInput(self):
        data = self.getData()
        return (
            data['atividade_ids']
            and
            data['usuario_uuid']
            and
            data['prioridade'] is not None
        )

    def getData(self):
        # SAP 3.0: POST /fila_prioritaria recebe a lista de atividades, o uuid
        # da pessoa e a prioridade.
        atividadeId = self.atividadeCb.itemData(self.atividadeCb.currentIndex())
        prioridade = self.prioridadeLe.text()
        return {
            'atividade_ids': [atividadeId] if atividadeId else [],
            'usuario_uuid': self.usuarioCb.itemData(self.usuarioCb.currentIndex()),
            'prioridade': int(prioridade) if prioridade else None
        }

    def setData(self, data):
        pass

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        message = self.sap.createFilaPrioritaria(
            self.getData()
        )
        self.accept()
        message and self.showInfo('Aviso', message)
        self.save.emit()

    @QtCore.pyqtSlot(int)
    def on_projetoCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.loteCb.clear()
            return
        self.loadLotes(self.projetoCb.currentText())

    def loadLotes(self, projectName):
        steps = self.controller.getSapStepsByTag(tag='lote', sortByTag='lote', tagFilter=('projeto', projectName))
        self.loadCombo(self.loteCb, [
            {'id': i['lote_id'], 'value': i['lote']}
            for i in steps
            if not i['linha_producao_id'] in [5] # EDGV 2.1.3
        ])
    
    @QtCore.pyqtSlot(int)
    def on_loteCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.linhaProducaoCb.clear()
            return
        self.loadLinhaProducao(self.loteCb.itemData(currentIndex))
    
    def loadLinhaProducao(self, loteId):
        steps = self.controller.getSapStepsByTag(tag='linha_producao', sortByTag='linha_producao', tagFilter=('lote_id', loteId))
        self.loadCombo(self.linhaProducaoCb, [
            {'id': i['linha_producao_id'], 'value': i['linha_producao']} 
            for i in steps
        ])

    @QtCore.pyqtSlot(int)
    def on_linhaProducaoCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.subfaseCb.clear()
            return
        self.loadSubfases(self.linhaProducaoCb.itemData(currentIndex))
   
    def loadSubfases(self, linhaProducaoId):
        subfases = self.controller.getSapStepsByTag(tag='subfase_id', sortByTag='subfase', tagFilter=('linha_producao_id', linhaProducaoId))
        subfases.sort(key=lambda item: int(item['subfase_id']), reverse=True)  
        self.loadCombo(self.subfaseCb, [
            {'id': i['subfase_id'], 'value': i['subfase']} 
            for i in subfases
        ])

    @QtCore.pyqtSlot(int)
    def on_subfaseCb_currentIndexChanged(self, currentIndex):
        if currentIndex < 1:
            self.atividadeCb.clear()
            return
        self.loadAtivdades(
            self.subfaseCb.itemText(currentIndex), 
            self.linhaProducaoCb.itemText(self.linhaProducaoCb.currentIndex())
        )

    def loadAtivdades(self, subfase, linhaProducao):
        atividades = self.sap.getRunningActivities()
        atividades = [
            a for a in atividades
            if a['linha_producao_nome'] == linhaProducao and a['subfase_nome'] == subfase
        ]
        atividades.sort(key=lambda item: int(item['atividade_id']))  
        self.loadCombo(self.atividadeCb, [
            {'id': i['atividade_id'], 'value': str(i['atividade_id'])} 
            for i in atividades
        ])

    