# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets
from SAP_Gerente.widgets.mMetadadoBase import MMetadadoLoteAlvo


class MResponsavelFase(MMetadadoLoteAlvo):
    """Associa um usuario de metadado como responsavel por uma fase, por LOTE
    (recomendado) ou por PRODUTO (excecao)."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(MResponsavelFase, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.usuarios = []
        self.fases = []
        self.registros = []
        self.setWindowTitle('Responsável por Fase (por lote ou produto)')
        self.setMinimumWidth(700)
        self._loadAux()
        self._buildUi()
        self._loadLotes()

    def _loadAux(self):
        try:
            self.usuarios = self.sap.getMetadadoUsuarios() or []
        except Exception:
            self.usuarios = []
        try:
            self.fases = self.sap.getPhases() or []
        except Exception:
            self.fases = []

    def _faseLabel(self, f):
        partes = [f.get('fase'), f.get('tipo_fase'), f.get('nome')]
        label = next((p for p in partes if p), None) or 'Fase {0}'.format(f.get('id'))
        lp = f.get('linha_producao')
        return '{0} - {1}'.format(label, lp) if lp else str(label)

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
        self.alvoCombo.currentIndexChanged.connect(self._fetch)
        form.addRow('Alvo:', self.alvoCombo)
        layout.addLayout(form)

        self.tabela = QtWidgets.QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(['id', 'usuário', 'fase'])
        self.tabela.setColumnHidden(0, True)
        self.tabela.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.tabela)

        addForm = QtWidgets.QFormLayout()
        self.usuarioCombo = QtWidgets.QComboBox()
        for u in self.usuarios:
            self.usuarioCombo.addItem(str(u.get('nome') or u.get('id')), u.get('id'))
        addForm.addRow('Usuário (metadado):', self.usuarioCombo)
        self.faseCombo = QtWidgets.QComboBox()
        for f in self.fases:
            self.faseCombo.addItem(self._faseLabel(f), f.get('id'))
        addForm.addRow('Fase:', self.faseCombo)
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
        chave = 'produto_id' if self._destino() == 'produto' else 'lote_id'
        try:
            todos = self.sap.getResponsavelFaseProduto() or []
        except Exception:
            todos = []
        self.registros = [r for r in todos if r.get(chave) == alvoId]
        for r in self.registros:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [r.get('id'), r.get('nome'), r.get('tipo_fase')]
            for col, v in enumerate(valores):
                self.tabela.setItem(row, col, QtWidgets.QTableWidgetItem('' if v is None else str(v)))
        self.tabela.resizeColumnsToContents()

    def _adicionar(self):
        alvoId = self.alvoCombo.currentData()
        if not alvoId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um alvo (lote ou produto).')
            return
        usuarioId = self.usuarioCombo.currentData()
        faseId = self.faseCombo.currentData()
        if usuarioId is None or faseId is None:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione usuário e fase (cadastre usuário de metadado antes).')
            return
        campos = {'usuario_id': usuarioId, 'fase_id': faseId}
        if self._destino() == 'produto':
            campos['produto_id'] = alvoId
        else:
            campos['lote_id'] = alvoId
        try:
            message = self.sap.criaResponsavelFaseProduto([campos])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._fetch()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))

    def _remover(self):
        row = self.tabela.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um responsável na tabela.')
            return
        item = self.tabela.item(row, 0)
        if not item or not item.text():
            return
        if not QtWidgets.QMessageBox.question(self, 'Atenção', 'Remover o responsável selecionado?'):
            return
        try:
            message = self.sap.deletaResponsavelFaseProduto([int(item.text())])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._fetch()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
