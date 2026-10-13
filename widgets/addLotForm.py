import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2


def carregarPeriodo(form, data):
    """Preenche os QDateEdit do período a partir de 'AAAA-MM-DD' (ou nulo)."""
    hoje = QtCore.QDate.currentDate()
    inicio = QtCore.QDate.fromString(str(data.get('data_inicio') or '')[:10], 'yyyy-MM-dd')
    form.dataInicioDe.setDate(inicio if inicio.isValid() else hoje)
    fim = QtCore.QDate.fromString(str(data.get('data_fim') or '')[:10], 'yyyy-MM-dd')
    form.semDataFimCkb.setChecked(not fim.isValid())
    form.dataFimDe.setDate(fim if fim.isValid() else hoje)


def lerPeriodo(form):
    """O período no formato do SAP 3.0: dia de calendário ISO, fim nulo se aberto."""
    return {
        'data_inicio': form.dataInicioDe.date().toString('yyyy-MM-dd'),
        'data_fim': None if form.semDataFimCkb.isChecked() else form.dataFimDe.date().toString('yyyy-MM-dd')
    }

class AddLotForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddLotForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Lote')
        # SAP 3.0: o lote é do ACERVO (acervo.lote). Não tem linha de produção
        # (o par lote/linha nasce da etapa), nem escala (a escala é da folha),
        # nem nome abreviado; tem PIT e período.
        self.loadCombo(self.projectsCb, [{'id': i['id'], 'value': i['nome']} for i in self.sap.getProjects()])
        carregarPeriodo(self, {})
        self.semDataFimCkb.toggled.connect(lambda checked: self.dataFimDe.setEnabled(not checked))
        self.dataFimDe.setEnabled(False)
        self.loadCombo(
            self.statusCb, 
            [
                {'id': i['code'], 'value': i['nome']} 
                for i in self.sap.getStatusDomain()
            ]
        )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addLotForm.ui'
        )

    def validInput(self):
        return (
            self.nameLe.text()
            and
            self.pitLe.text()
            and
            self.projectsCb.itemData(self.projectsCb.currentIndex())
            and
            self.statusCb.itemData(self.statusCb.currentIndex())
        )

    def getData(self):
        data = {
            'nome': self.nameLe.text(),
            'pit': self.pitLe.text(),
            'descricao': self.descriptionTe.toPlainText(),
            'projeto_id': self.projectsCb.itemData(self.projectsCb.currentIndex()),
            'status_execucao_id': self.statusCb.itemData(self.statusCb.currentIndex())
        }
        data.update(lerPeriodo(self))
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.nameLe.setText(data['nome'])
        self.pitLe.setText(data.get('pit') or '')
        self.descriptionTe.setPlainText(data.get('descricao') or '')
        carregarPeriodo(self, data)
        if self.projectsCb.findData(data['projeto_id']) < 0:
            # projeto encerrado: entra no combo para o lote poder ser editado
            self.projectsCb.addItem(data.get('projeto') or str(data['projeto_id']), data['projeto_id'])
        self.projectsCb.setCurrentIndex(self.projectsCb.findData(data['projeto_id']))
        self.statusCb.setCurrentIndex(self.statusCb.findData(data['status_execucao_id']))
        
    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha nome, PIT, projeto e status!')
            return
        data = [self.getData()]
        if self.isEditMode():
            message = self.sap.updateLots(
                data
            )
        else:
            message = self.sap.createLots(
                data
            )
        self.accept()
        message and self.showInfo('Aviso', message)
        self.save.emit()