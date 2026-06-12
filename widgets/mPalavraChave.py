# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets
from SAP_Gerente.widgets.mMetadadoBase import MLoteComboDialog


class MPalavraChave(MLoteComboDialog):
    """Cadastro de palavras-chave do produto (ISO 19115). Keyword e EXCLUSIVAMENTE
    nivel produto (nao tem nivel lote): toponimia e descricao sao por folha. O lote
    serve apenas para listar os produtos; o cadastro e sempre por produto."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(MPalavraChave, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.tipos = []
        self.registros = []
        self.setWindowTitle('Palavras-chave do Produto (por produto)')
        self.setMinimumWidth(640)
        self._loadAux()
        self._buildUi()
        self._loadLotes()

    def _loadAux(self):
        try:
            self.tipos = self.sap.getMetadadoTipoPalavraChave() or []
        except Exception:
            self.tipos = []

    def _loadAlvos(self):
        loteId = self.loteCombo.currentData()
        self.alvoCombo.clear()
        if not loteId:
            return
        try:
            produtos = self.sap.getProdutosDoLote(loteId) or []
        except Exception:
            produtos = []
        for p in produtos:
            label = p.get('inom') or p.get('mi') or p.get('nome') or str(p.get('id'))
            self.alvoCombo.addItem(str(label), p.get('id'))

    def _buildUi(self):
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        self.loteCombo = QtWidgets.QComboBox()
        self.loteCombo.currentIndexChanged.connect(self._loadAlvos)
        form.addRow('Lote:', self.loteCombo)

        self.alvoCombo = QtWidgets.QComboBox()
        self.alvoCombo.currentIndexChanged.connect(self._fetch)
        form.addRow('Produto:', self.alvoCombo)
        layout.addLayout(form)

        self.tabela = QtWidgets.QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(['id', 'palavra-chave', 'tipo'])
        self.tabela.setColumnHidden(0, True)
        self.tabela.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.tabela)

        addForm = QtWidgets.QFormLayout()
        self.nomeLe = QtWidgets.QLineEdit()
        addForm.addRow('Palavra-chave:', self.nomeLe)
        self.tipoCombo = QtWidgets.QComboBox()
        for t in self.tipos:
            self.tipoCombo.addItem(str(t.get('nome') or t.get('code')), t.get('code'))
        addForm.addRow('Tipo:', self.tipoCombo)
        layout.addLayout(addForm)

        btnLayout = QtWidgets.QHBoxLayout()
        self.adicionarBtn = QtWidgets.QPushButton('Adicionar')
        self.adicionarBtn.clicked.connect(self._adicionar)
        self.removerBtn = QtWidgets.QPushButton('Remover selecionado')
        self.removerBtn.clicked.connect(self._remover)
        btnLayout.addWidget(self.adicionarBtn)
        btnLayout.addWidget(self.removerBtn)
        btnLayout.addStretch()
        self.fecharBtn = QtWidgets.QPushButton('Fechar')
        self.fecharBtn.clicked.connect(self.close)
        btnLayout.addWidget(self.fecharBtn)
        layout.addLayout(btnLayout)

    def _fetch(self):
        alvoId = self.alvoCombo.currentData()
        self.tabela.setRowCount(0)
        if not alvoId:
            return
        try:
            todas = self.sap.getPalavraChaveProduto() or []
        except Exception:
            todas = []
        self.registros = [r for r in todas if r.get('produto_id') == alvoId]
        for r in self.registros:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [r.get('id'), r.get('nome'), r.get('tipo_palavra_chave')]
            for col, v in enumerate(valores):
                self.tabela.setItem(row, col, QtWidgets.QTableWidgetItem('' if v is None else str(v)))
        self.tabela.resizeColumnsToContents()

    def _adicionar(self):
        alvoId = self.alvoCombo.currentData()
        if not alvoId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um produto.')
            return
        nome = self.nomeLe.text().strip()
        tipoId = self.tipoCombo.currentData()
        if not nome or tipoId is None:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Preencha a palavra-chave e o tipo.')
            return
        campos = {'nome': nome, 'tipo_palavra_chave_id': tipoId, 'produto_id': alvoId}
        try:
            message = self.sap.criaPalavraChaveProduto([campos])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self.nomeLe.clear()
            self._fetch()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))

    def _remover(self):
        row = self.tabela.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione uma palavra-chave na tabela.')
            return
        item = self.tabela.item(row, 0)
        if not item or not item.text():
            return
        if QtWidgets.QMessageBox.question(self, 'Atenção', 'Remover a palavra-chave selecionada?') != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        try:
            message = self.sap.deletaPalavraChaveProduto([int(item.text())])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._fetch()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
