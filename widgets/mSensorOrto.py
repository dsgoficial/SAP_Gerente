# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets
from SAP_Gerente.widgets.mMetadadoBase import MMetadadoLoteAlvo


class MSensorOrto(MMetadadoLoteAlvo):
    """Cadastro dos sensores da carta ortoimagem (array "sensores" do JSON de
    edicao), por LOTE (recomendado) ou por PRODUTO (excecao). Lista os sensores
    do alvo e permite adicionar/remover."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(MSensorOrto, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.sensores = []
        self.setWindowTitle('Sensores da Carta Ortoimagem (por lote ou produto)')
        self.setMinimumWidth(700)
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
        self.alvoCombo.currentIndexChanged.connect(self._loadSensores)
        form.addRow('Alvo:', self.alvoCombo)
        layout.addLayout(form)

        self.tabela = QtWidgets.QTableWidget(0, 7)
        self.tabela.setHorizontalHeaderLabels(
            ['id', 'tipo', 'plataforma', 'nome', 'resolução', 'bandas', 'nível']
        )
        self.tabela.setColumnHidden(0, True)
        self.tabela.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.tabela)

        addForm = QtWidgets.QFormLayout()
        self.tipoLe = QtWidgets.QLineEdit()
        addForm.addRow('Tipo:', self.tipoLe)
        self.plataformaLe = QtWidgets.QLineEdit()
        addForm.addRow('Plataforma:', self.plataformaLe)
        self.nomeLe = QtWidgets.QLineEdit()
        addForm.addRow('Nome:', self.nomeLe)
        self.resolucaoLe = QtWidgets.QLineEdit()
        addForm.addRow('Resolução:', self.resolucaoLe)
        self.bandasLe = QtWidgets.QLineEdit()
        addForm.addRow('Bandas:', self.bandasLe)
        self.nivelLe = QtWidgets.QLineEdit()
        addForm.addRow('Nível do produto:', self.nivelLe)
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

    def _loadSensores(self):
        alvoId = self.alvoCombo.currentData()
        self.tabela.setRowCount(0)
        if not alvoId:
            return
        chave = 'produto_id' if self._destino() == 'produto' else 'lote_id'
        try:
            todos = self.sap.getSensorCartaOrtoimagem() or []
        except Exception:
            todos = []
        self.sensores = [s for s in todos if s.get(chave) == alvoId]
        for s in self.sensores:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [
                s.get('id'), s.get('tipo'), s.get('plataforma'), s.get('nome'),
                s.get('resolucao'), s.get('bandas'), s.get('nivel_produto')
            ]
            for col, v in enumerate(valores):
                self.tabela.setItem(row, col, QtWidgets.QTableWidgetItem('' if v is None else str(v)))
        self.tabela.resizeColumnsToContents()

    def _adicionar(self):
        alvoId = self.alvoCombo.currentData()
        if not alvoId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um alvo (lote ou produto).')
            return
        campos = {
            'tipo': self.tipoLe.text().strip(),
            'plataforma': self.plataformaLe.text().strip(),
            'nome': self.nomeLe.text().strip(),
            'resolucao': self.resolucaoLe.text().strip(),
            'bandas': self.bandasLe.text().strip(),
            'nivel_produto': self.nivelLe.text().strip()
        }
        if not all(campos.values()):
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Preencha todos os campos do sensor.')
            return
        if self._destino() == 'produto':
            campos['produto_id'] = alvoId
        else:
            campos['lote_id'] = alvoId
        try:
            message = self.sap.criaSensorCartaOrtoimagem([campos])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            for le in [self.tipoLe, self.plataformaLe, self.nomeLe,
                       self.resolucaoLe, self.bandasLe, self.nivelLe]:
                le.clear()
            self._loadSensores()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))

    def _remover(self):
        row = self.tabela.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um sensor na tabela.')
            return
        item = self.tabela.item(row, 0)
        if not item or not item.text():
            return
        sensorId = int(item.text())
        if not QtWidgets.QMessageBox.question(self, 'Atenção', 'Remover o sensor selecionado?'):
            return
        try:
            message = self.sap.deletaSensorCartaOrtoimagem([sensorId])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._loadSensores()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
