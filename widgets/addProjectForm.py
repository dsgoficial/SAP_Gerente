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

class AddProjectForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddProjectForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Projeto')
        self.loadStatusCombo()
        # SAP 3.0: o projeto é do ACERVO (acervo.projeto), sem nome abreviado
        # e com período.
        carregarPeriodo(self, {})
        self.semDataFimCkb.toggled.connect(lambda checked: self.dataFimDe.setEnabled(not checked))
        self.dataFimDe.setEnabled(False)

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
            self.statusCb.currentIndex() > 0  # Ensure a status is selected
        )

    def getData(self):
        data = {
            'nome': self.nameLe.text(),
            'descricao': self.descriptionTe.toPlainText(),
            'status_execucao_id': self.statusCb.currentData()
        }
        data.update(lerPeriodo(self))
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.nameLe.setText(data['nome'])
        self.descriptionTe.setPlainText(data['descricao'] or '')
        carregarPeriodo(self, data)

        # Set the status in the combo box
        status_index = self.statusCb.findData(data['status_execucao_id'])
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
        message and self.showInfo('Aviso', message)
        self.save.emit()