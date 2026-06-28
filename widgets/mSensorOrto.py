# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets
from SAP_Gerente.widgets.mMetadadoBase import MMetadadoLoteAlvo


class MSensorOrto(MMetadadoLoteAlvo):
    """Cadastro dos sensores da carta ortoimagem (array "sensores" do JSON de
    edicao), por LOTE (recomendado) ou por PRODUTO (excecao). Lista os sensores
    do alvo e permite adicionar/remover."""

    TIPO_OPCOES = ['', 'Óptico', 'SAR', 'Multiespectral', 'Pancromático']
    PLATAFORMA_OPCOES = ['', 'Satélite', 'Aeronave', 'VANT/Drone']
    NIVEL_OPCOES = ['', 'Ortorretificado', 'Georreferenciado', 'Bruto']
    # Combos editaveis (lista comum + texto livre): padronizam a grafia/formato,
    # sem fechar o dominio (sensor ou banda fora da lista pode ser digitado).
    NOME_OPCOES = ['', 'WorldView-3', 'WorldView-2', 'GeoEye-1', 'Pléiades-1A',
                   'Pléiades-1B', 'Pléiades Neo', 'Sentinel-2', 'CBERS-4A', 'SPOT-7']
    BANDAS_OPCOES = ['', 'PAN', 'R,G,B', 'R,G,B,NIR', 'R,G,B,NIR,RedEdge']

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

        self.showFinishedCheckBox = QtWidgets.QCheckBox('Mostrar lotes finalizados')
        self.showFinishedCheckBox.toggled.connect(self._loadLotes)
        form.addRow('', self.showFinishedCheckBox)

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
        self.tipoLe = QtWidgets.QComboBox()
        self.tipoLe.setEditable(True)
        self.tipoLe.addItems(self.TIPO_OPCOES)
        addForm.addRow('Tipo:', self.tipoLe)
        self.plataformaLe = QtWidgets.QComboBox()
        self.plataformaLe.setEditable(True)
        self.plataformaLe.addItems(self.PLATAFORMA_OPCOES)
        addForm.addRow('Plataforma:', self.plataformaLe)
        self.nomeLe = QtWidgets.QComboBox()
        self.nomeLe.setEditable(True)
        self.nomeLe.addItems(self.NOME_OPCOES)
        addForm.addRow('Nome:', self.nomeLe)
        self.resolucaoLe = QtWidgets.QLineEdit()
        self.resolucaoLe.setPlaceholderText('GSD real, ex.: 0,31 m')
        addForm.addRow('Resolução:', self.resolucaoLe)
        self.bandasLe = QtWidgets.QComboBox()
        self.bandasLe.setEditable(True)
        self.bandasLe.addItems(self.BANDAS_OPCOES)
        addForm.addRow('Bandas:', self.bandasLe)
        self.nivelLe = QtWidgets.QComboBox()
        self.nivelLe.setEditable(True)
        self.nivelLe.addItems(self.NIVEL_OPCOES)
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
            'tipo': self.tipoLe.currentText().strip(),
            'plataforma': self.plataformaLe.currentText().strip(),
            'nome': self.nomeLe.currentText().strip(),
            'resolucao': self.resolucaoLe.text().strip(),
            'bandas': self.bandasLe.currentText().strip(),
            'nivel_produto': self.nivelLe.currentText().strip()
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
            self.tipoLe.setCurrentText('')
            self.plataformaLe.setCurrentText('')
            self.nomeLe.setCurrentText('')
            self.resolucaoLe.clear()
            self.bandasLe.setCurrentText('')
            self.nivelLe.setCurrentText('')
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
        if QtWidgets.QMessageBox.question(self, 'Atenção', 'Remover o sensor selecionado?') != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        try:
            message = self.sap.deletaSensorCartaOrtoimagem([sensorId])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._loadSensores()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
