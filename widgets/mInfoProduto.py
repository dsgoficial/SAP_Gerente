# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets
from SAP_Gerente.widgets.mMetadadoBase import MMetadadoLoteAlvo


class MInfoProduto(MMetadadoLoteAlvo):
    """Preenche metadado.informacoes_produto (ISO 19115: datum, especificacao,
    sigilo, restricoes, organizacoes, responsavel, linhagem) por LOTE
    (recomendado) ou por PRODUTO (excecao). Alimenta o datum_vertical e a
    especificacao_representacao do JSON de edicao e o XML de metadados. Upsert."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(MInfoProduto, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.registros = []
        self.restricoes = []
        self.classificacoes = []
        self.organizacoes = []
        self.datums = []
        self.especificacoes = []
        self.usuarios = []
        self.currentId = None
        self.setWindowTitle('Informações do Produto (por lote ou produto)')
        self.setMinimumWidth(660)
        self._loadAux()
        self._buildUi()
        self._loadLotes()

    def _loadAux(self):
        getters = {
            'restricoes': self.sap.getMetadadoCodigoRestricao,
            'classificacoes': self.sap.getMetadadoCodigoClassificacao,
            'organizacoes': self.sap.getMetadadoOrganizacao,
            'datums': self.sap.getMetadadoDatumVertical,
            'especificacoes': self.sap.getMetadadoEspecificacao,
            'usuarios': self.sap.getMetadadoUsuarios
        }
        for attr, fn in getters.items():
            try:
                setattr(self, attr, fn() or [])
            except Exception:
                setattr(self, attr, [])
        try:
            self.registros = self.sap.getInformacoesProduto() or []
        except Exception:
            self.registros = []

    def _fillCombo(self, combo, itens, valueKey='code'):
        combo.clear()
        for it in itens:
            combo.addItem(str(it.get('nome') or it.get(valueKey)), it.get(valueKey))

    def _buildUi(self):
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        self.loteCombo = QtWidgets.QComboBox()
        self.loteCombo.currentIndexChanged.connect(self._loadAlvos)
        form.addRow('Lote:', self.loteCombo)

        self.showFinishedCheckBox = QtWidgets.QCheckBox('Mostrar lotes finalizados')
        self.showFinishedCheckBox.toggled.connect(self._loadLotes)
        form.addRow('', self.showFinishedCheckBox)

        self.destinoCombo = QtWidgets.QComboBox()
        self.destinoCombo.addItem('Lote (recomendado)', 'lote')
        self.destinoCombo.addItem('Produto (exceção)', 'produto')
        self.destinoCombo.currentIndexChanged.connect(self._loadAlvos)
        form.addRow('Preencher por:', self.destinoCombo)

        self.alvoCombo = QtWidgets.QComboBox()
        self.alvoCombo.currentIndexChanged.connect(self._prefill)
        form.addRow('Alvo:', self.alvoCombo)

        self.resumoTe = QtWidgets.QPlainTextEdit()
        self.resumoTe.setFixedHeight(50)
        form.addRow('Resumo:', self.resumoTe)
        self.propositoTe = QtWidgets.QPlainTextEdit()
        self.propositoTe.setFixedHeight(50)
        form.addRow('Propósito:', self.propositoTe)
        self.creditosTe = QtWidgets.QPlainTextEdit()
        self.creditosTe.setFixedHeight(50)
        form.addRow('Créditos:', self.creditosTe)
        self.infoCompTe = QtWidgets.QPlainTextEdit()
        self.infoCompTe.setFixedHeight(50)
        form.addRow('Informações complementares:', self.infoCompTe)
        self.linhagemTe = QtWidgets.QPlainTextEdit()
        self.linhagemTe.setFixedHeight(50)
        form.addRow('Declaração de linhagem:', self.linhagemTe)
        self.projetoBdgexLe = QtWidgets.QLineEdit()
        form.addRow('Projeto BDGEx:', self.projetoBdgexLe)

        self.limitacaoAcessoCombo = QtWidgets.QComboBox()
        self._fillCombo(self.limitacaoAcessoCombo, self.restricoes)
        form.addRow('Limitação de acesso:', self.limitacaoAcessoCombo)
        self.limitacaoUsoCombo = QtWidgets.QComboBox()
        self._fillCombo(self.limitacaoUsoCombo, self.restricoes)
        form.addRow('Limitação de uso:', self.limitacaoUsoCombo)
        self.restricaoUsoCombo = QtWidgets.QComboBox()
        self._fillCombo(self.restricaoUsoCombo, self.restricoes)
        form.addRow('Restrição de uso:', self.restricaoUsoCombo)
        self.grauSigiloCombo = QtWidgets.QComboBox()
        self._fillCombo(self.grauSigiloCombo, self.classificacoes)
        form.addRow('Grau de sigilo:', self.grauSigiloCombo)
        self.orgRespCombo = QtWidgets.QComboBox()
        self._fillCombo(self.orgRespCombo, self.organizacoes)
        form.addRow('Organização responsável:', self.orgRespCombo)
        self.orgDistCombo = QtWidgets.QComboBox()
        self._fillCombo(self.orgDistCombo, self.organizacoes)
        form.addRow('Organização de distribuição:', self.orgDistCombo)
        self.datumCombo = QtWidgets.QComboBox()
        self._fillCombo(self.datumCombo, self.datums)
        form.addRow('Datum vertical:', self.datumCombo)
        self.especificacaoCombo = QtWidgets.QComboBox()
        self._fillCombo(self.especificacaoCombo, self.especificacoes)
        form.addRow('Especificação:', self.especificacaoCombo)
        self.responsavelCombo = QtWidgets.QComboBox()
        for u in self.usuarios:
            self.responsavelCombo.addItem(str(u.get('nome') or u.get('id')), u.get('id'))
        form.addRow('Responsável pelo produto:', self.responsavelCombo)

        layout.addLayout(form)

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addStretch()
        self.salvarBtn = QtWidgets.QPushButton('Salvar')
        self.salvarBtn.clicked.connect(self._salvar)
        self.fecharBtn = QtWidgets.QPushButton('Fechar')
        self.fecharBtn.clicked.connect(self.close)
        btnLayout.addWidget(self.salvarBtn)
        btnLayout.addWidget(self.fecharBtn)
        layout.addLayout(btnLayout)

    def _findRegistro(self, alvoId):
        chave = 'produto_id' if self._destino() == 'produto' else 'lote_id'
        for r in self.registros:
            if r.get(chave) == alvoId:
                return r
        return None

    def _setCombo(self, combo, value):
        idx = combo.findData(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _prefill(self):
        alvoId = self.alvoCombo.currentData()
        self.currentId = None
        if not alvoId:
            return
        r = self._findRegistro(alvoId)
        if not r:
            return
        self.currentId = r.get('id')
        self.resumoTe.setPlainText(str(r.get('resumo') or ''))
        self.propositoTe.setPlainText(str(r.get('proposito') or ''))
        self.creditosTe.setPlainText(str(r.get('creditos') or ''))
        self.infoCompTe.setPlainText(str(r.get('informacoes_complementares') or ''))
        self.linhagemTe.setPlainText(str(r.get('declaracao_linhagem') or ''))
        self.projetoBdgexLe.setText(str(r.get('projeto_bdgex') or ''))
        self._setCombo(self.limitacaoAcessoCombo, r.get('limitacao_acesso_id'))
        self._setCombo(self.limitacaoUsoCombo, r.get('limitacao_uso_id'))
        self._setCombo(self.restricaoUsoCombo, r.get('restricao_uso_id'))
        self._setCombo(self.grauSigiloCombo, r.get('grau_sigilo_id'))
        self._setCombo(self.orgRespCombo, r.get('organizacao_responsavel_id'))
        self._setCombo(self.orgDistCombo, r.get('organizacao_distribuicao_id'))
        self._setCombo(self.datumCombo, r.get('datum_vertical_id'))
        self._setCombo(self.especificacaoCombo, r.get('especificacao_id'))
        self._setCombo(self.responsavelCombo, r.get('responsavel_produto_id'))

    def _salvar(self):
        alvoId = self.alvoCombo.currentData()
        if not alvoId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um alvo (lote ou produto).')
            return
        if self.responsavelCombo.currentData() is None:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Cadastre/escolha um responsável (usuário de metadado).')
            return
        data = {
            'resumo': self.resumoTe.toPlainText().strip(),
            'proposito': self.propositoTe.toPlainText().strip(),
            'creditos': self.creditosTe.toPlainText().strip(),
            'informacoes_complementares': self.infoCompTe.toPlainText().strip(),
            'declaracao_linhagem': self.linhagemTe.toPlainText().strip(),
            'projeto_bdgex': self.projetoBdgexLe.text().strip(),
            'limitacao_acesso_id': self.limitacaoAcessoCombo.currentData(),
            'limitacao_uso_id': self.limitacaoUsoCombo.currentData(),
            'restricao_uso_id': self.restricaoUsoCombo.currentData(),
            'grau_sigilo_id': self.grauSigiloCombo.currentData(),
            'organizacao_responsavel_id': self.orgRespCombo.currentData(),
            'organizacao_distribuicao_id': self.orgDistCombo.currentData(),
            'datum_vertical_id': self.datumCombo.currentData(),
            'especificacao_id': self.especificacaoCombo.currentData(),
            'responsavel_produto_id': self.responsavelCombo.currentData()
        }
        if self._destino() == 'produto':
            data['produto_id'] = alvoId
        else:
            data['lote_id'] = alvoId
        try:
            if self.currentId:
                data['id'] = self.currentId
                message = self.sap.atualizaInformacoesProduto([data])
            else:
                message = self.sap.criaInformacoesProduto([data])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._loadAux()
            self._prefill()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
