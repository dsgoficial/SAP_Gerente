import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2
from SAP_Gerente.modules.sap.api.contrato import TIPO_DADO_BASE_VERSIONADA

class AddProductionDataForm(InputDialogV2):

    # Toda produção é base versionada (decisão do chefe, 2026-10-15): o dado
    # de produção é só o identificador da base no serviço (o `repo_id`), sem
    # tipo a escolher, sem IP, porta, banco nem teste de conexão. O tipo vai 4
    # fixo no corpo, porque o servidor ainda exige a chave no Joi.

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddProductionDataForm, self).__init__(parent=parent)
        self.sap = sap
        self.setWindowTitle('Adicionar Base Versionada')
        self.carregarRepos()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProductionDataForm.ui'
        )

    def carregarRepos(self):
        # A lista vem do repasse do SAP quando o gerente pode lê-la; senão
        # (403, sem caixa de erro) o `repo_id` é digitado.
        atual = self.repoCb.currentText()
        repos = self.sap.getVersionamentoRepos()
        # A base é a raiz (sem pai): lote, bloco e atividade são clones dela.
        bases = [r for r in repos if not r.get('parent_id')] or repos
        self.repoCb.clear()
        for repo in bases:
            rotulo = repo.get('label') or ''
            texto = '{0} - {1}'.format(repo['id'], rotulo) if rotulo else repo['id']
            self.repoCb.addItem(texto, repo['id'])
        self.repoCb.setEditText(atual)

    def getRepoId(self):
        texto = self.repoCb.currentText().strip()
        idx = self.repoCb.findText(texto)
        if idx >= 0 and self.repoCb.itemData(idx):
            return self.repoCb.itemData(idx)
        return texto

    def validInput(self):
        return bool(self.getRepoId())

    def getData(self):
        data = {
            'configuracao_producao': self.getRepoId(),
            'tipo_dado_producao_id': TIPO_DADO_BASE_VERSIONADA
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.repoCb.setEditText(data.get('configuracao_producao') or '')

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Informe a base no serviço (repo_id)!')
            return
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
            data = [self.getData()]
            if self.isEditMode():
                message = self.sap.updateProductionData(
                    data
                )
            else:
                message = self.sap.createProductionData(
                    data
                )
            QtWidgets.QApplication.restoreOverrideCursor()
            self.accept()
            message and self.showInfo('Aviso', message)
            self.save.emit()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Erro', str(e))
