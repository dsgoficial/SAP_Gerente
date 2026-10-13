import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2
from SAP_Gerente.modules.sap.api.contrato import TIPO_DADO_BASE_VERSIONADA
from .testDatabase  import TestDatabase
import re

class AddProductionDataForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddProductionDataForm, self).__init__(parent=parent)
        self.sap = sap
        self.reposCarregados = False
        self.setWindowTitle('Adicionar Banco de Dados de Produção')
        self.criarCampoRepo()
        self.loadCombo(self.typeProductionDataCb, [{'id': i['code'], 'value': i['nome']} for i in self.sap.getProductionDataType()])
        self.typeProductionDataCb.currentIndexChanged.connect(self.atualizarCampos)
        self.atualizarCampos()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addProductionDataForm.ui'
        )

    def criarCampoRepo(self):
        # Tipo 4 'Base versionada': só o identificador da base no serviço (o
        # `repo_id`), sem IP, porta, banco nem teste de conexão. A lista vem do
        # repasse do SAP quando o gerente pode lê-la; senão o campo é digitado.
        self.repoLabel = QtWidgets.QLabel('Base no serviço (repo_id):', self)
        self.repoCb = QtWidgets.QComboBox(self)
        self.repoCb.setEditable(True)
        self.repoCb.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.repoCb.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.repoLayout = QtWidgets.QHBoxLayout()
        self.repoLayout.addWidget(self.repoLabel)
        self.repoLayout.addWidget(self.repoCb)
        # O campo entra acima dos botões: a linha dos botões desce uma posição.
        self.gridLayout.removeItem(self.horizontalLayout)
        self.gridLayout.addLayout(self.repoLayout, 4, 0)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0)

    def getTipo(self):
        return self.typeProductionDataCb.itemData(self.typeProductionDataCb.currentIndex())

    def isBaseVersionada(self):
        return self.getTipo() == TIPO_DADO_BASE_VERSIONADA

    def atualizarCampos(self, *args):
        versionada = self.isBaseVersionada()
        for widget in (
                self.label, self.ipDBLe,
                self.label_2, self.portDBLe,
                self.label_3, self.nameDBLe
            ):
            widget.setVisible(not versionada)
        self.repoLabel.setVisible(versionada)
        self.repoCb.setVisible(versionada)
        if versionada and not self.reposCarregados:
            self.carregarRepos()

    def carregarRepos(self):
        self.reposCarregados = True
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
        if self.isBaseVersionada():
            return bool(self.getRepoId())
        return (
            self.ipDBLe.text()
            and
            self.portDBLe.text()
            and
            self.nameDBLe.text()
            and
            self.typeProductionDataCb.itemData(self.typeProductionDataCb.currentIndex())            
        )

    def getData(self):
        if self.isBaseVersionada():
            configuracao = self.getRepoId()
        else:
            configuracao = "{}:{}/{}".format(
                self.ipDBLe.text(),
                self.portDBLe.text(),
                self.nameDBLe.text()
            )
        data = {
            'configuracao_producao': configuracao,
            'tipo_dado_producao_id': self.typeProductionDataCb.itemData(self.typeProductionDataCb.currentIndex())
        }
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def setData(self, data):
        self.setCurrentId(data['id'])
        self.typeProductionDataCb.setCurrentIndex(self.typeProductionDataCb.findData(data['tipo_dado_producao_id']))
        if data['tipo_dado_producao_id'] == TIPO_DADO_BASE_VERSIONADA:
            self.repoCb.setEditText(data.get('configuracao_producao') or '')
            return
        self.ipDBLe.setText(data['configuracao_producao'].split('/')[0].split(':')[0])
        self.portDBLe.setText(data['configuracao_producao'].split('/')[0].split(':')[1])
        self.nameDBLe.setText(data['configuracao_producao'].split('/')[-1])
    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    def hasDatabase(self):
        result = TestDatabase(
            self.ipDBLe.text(),
            self.portDBLe.text(),
            self.nameDBLe.text(),
            self
        ).exec()
        return QtWidgets.QDialog.DialogCode.Accepted == result
    
    def checkDatabaseName(self):
        nameDB = self.nameDBLe.text()
        regex = re.compile(r'[\.@!#$%^&*()<>?/\|}{~:]')
        if  (
                nameDB[0].isdigit()
                or
                len([l for l in nameDB if l.isupper()]) > 0
                or
                regex.search(nameDB)
            ):
            return False
        return True

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha todos os campos!')
            return
        # A base versionada não é banco: nem nome de banco nem teste psycopg2.
        if not self.isBaseVersionada():
            if not self.checkDatabaseName():
                self.showError('Aviso', 'Nome do banco inválido!')
                return
            if not self.hasDatabase():
                self.showError('Aviso', 'Sem conexão com o banco!')
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
        