# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets
from SAP_Gerente.widgets.mMetadadoBase import MMetadadoLoteAlvo


class MImagensOrto(MMetadadoLoteAlvo):
    """Cadastro das imagens de fundo da carta ortoimagem (array "imagens" do JSON
    de edicao), por LOTE (recomendado) ou por PRODUTO (excecao)."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(MImagensOrto, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.imagens = []
        self.setWindowTitle('Imagens da Carta Ortoimagem (por lote ou produto)')
        self.setMinimumWidth(720)
        self._buildUi()
        self._loadLotes()

    def _buildUi(self):
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        self.loteCombo = QtWidgets.QComboBox()
        self.loteCombo.currentIndexChanged.connect(self._loadAlvos)
        form.addRow('Lote:', self.loteCombo)

        self.destinoCombo = QtWidgets.QComboBox()
        self.destinoCombo.addItem('Lote (recomendado)', 'lote')
        self.destinoCombo.addItem('Produto (exceção)', 'produto')
        self.destinoCombo.currentIndexChanged.connect(self._loadAlvos)
        form.addRow('Cadastrar por:', self.destinoCombo)

        self.alvoCombo = QtWidgets.QComboBox()
        self.alvoCombo.currentIndexChanged.connect(self._loadImagens)
        form.addRow('Alvo:', self.alvoCombo)
        layout.addLayout(form)

        self.tabela = QtWidgets.QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(['id', 'caminho da imagem', 'estilo', 'EPSG'])
        self.tabela.setColumnHidden(0, True)
        self.tabela.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.tabela)

        addForm = QtWidgets.QFormLayout()
        self.caminhoImagemLe = QtWidgets.QLineEdit()
        self.caminhoImagemLe.setPlaceholderText('caminho absoluto, sem espaços')
        addForm.addRow('Caminho da imagem:', self.caminhoImagemLe)
        self.caminhoEstiloLe = QtWidgets.QLineEdit()
        self.caminhoEstiloLe.setPlaceholderText('opcional')
        addForm.addRow('Caminho do estilo:', self.caminhoEstiloLe)
        self.epsgLe = QtWidgets.QLineEdit()
        addForm.addRow('EPSG:', self.epsgLe)
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

    def _loadImagens(self):
        alvoId = self.alvoCombo.currentData()
        self.tabela.setRowCount(0)
        if not alvoId:
            return
        chave = 'produto_id' if self._destino() == 'produto' else 'lote_id'
        try:
            todas = self.sap.getImagensCartaOrtoimagem() or []
        except Exception:
            todas = []
        self.imagens = [i for i in todas if i.get(chave) == alvoId]
        for i in self.imagens:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [i.get('id'), i.get('caminho_imagem'), i.get('caminho_estilo'), i.get('epsg')]
            for col, v in enumerate(valores):
                self.tabela.setItem(row, col, QtWidgets.QTableWidgetItem('' if v is None else str(v)))
        self.tabela.resizeColumnsToContents()

    def _adicionar(self):
        alvoId = self.alvoCombo.currentData()
        if not alvoId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um alvo (lote ou produto).')
            return
        caminho = self.caminhoImagemLe.text().strip()
        epsg = self.epsgLe.text().strip()
        if not caminho or not epsg:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Preencha caminho da imagem e EPSG.')
            return
        campos = {
            'caminho_imagem': caminho,
            'caminho_estilo': self.caminhoEstiloLe.text().strip() or None,
            'epsg': epsg
        }
        if self._destino() == 'produto':
            campos['produto_id'] = alvoId
        else:
            campos['lote_id'] = alvoId
        try:
            message = self.sap.criaImagensCartaOrtoimagem([campos])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            for le in [self.caminhoImagemLe, self.caminhoEstiloLe, self.epsgLe]:
                le.clear()
            self._loadImagens()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))

    def _remover(self):
        row = self.tabela.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione uma imagem na tabela.')
            return
        item = self.tabela.item(row, 0)
        if not item or not item.text():
            return
        imagemId = int(item.text())
        if QtWidgets.QMessageBox.question(self, 'Atenção', 'Remover a imagem selecionada?') != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        try:
            message = self.sap.deletaImagensCartaOrtoimagem([imagemId])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._loadImagens()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
