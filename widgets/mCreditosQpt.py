# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets


class MCreditosQpt(QtWidgets.QDialog):
    """Cadastro dos creditos QPT (metadado.creditos_qpt), consumidos pela tela
    de Metadados de Edicao da Carta. Tabela global (id, nome, qpt): nao e por
    lote nem por produto. Selecionar uma linha carrega no formulario para
    edicao; o botao Salvar cria (sem selecao) ou atualiza (com selecao)."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(MCreditosQpt, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.registros = []
        self.currentId = None
        self.setWindowTitle('Créditos (QPT) — metadados')
        self.setMinimumWidth(640)
        self._buildUi()
        self._fetch()

    def _buildUi(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.tabela = QtWidgets.QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(['id', 'nome', 'qpt'])
        self.tabela.setColumnHidden(0, True)
        self.tabela.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.itemSelectionChanged.connect(self._onSelect)
        layout.addWidget(self.tabela)

        form = QtWidgets.QFormLayout()
        self.nomeLe = QtWidgets.QLineEdit()
        self.nomeLe.setPlaceholderText('identificação do crédito (ex.: Crédito padrão DSG)')
        form.addRow('Nome:', self.nomeLe)
        self.qptTe = QtWidgets.QPlainTextEdit()
        self.qptTe.setPlaceholderText('texto do crédito (QPT)')
        self.qptTe.setFixedHeight(100)
        form.addRow('QPT:', self.qptTe)
        layout.addLayout(form)

        btnLayout = QtWidgets.QHBoxLayout()
        self.novoBtn = QtWidgets.QPushButton('Novo')
        self.novoBtn.clicked.connect(self._novo)
        self.salvarBtn = QtWidgets.QPushButton('Salvar')
        self.salvarBtn.clicked.connect(self._salvar)
        self.removerBtn = QtWidgets.QPushButton('Remover selecionado')
        self.removerBtn.clicked.connect(self._remover)
        btnLayout.addWidget(self.novoBtn)
        btnLayout.addWidget(self.salvarBtn)
        btnLayout.addWidget(self.removerBtn)
        btnLayout.addStretch()
        self.fecharBtn = QtWidgets.QPushButton('Fechar')
        self.fecharBtn.clicked.connect(self.close)
        btnLayout.addWidget(self.fecharBtn)
        layout.addLayout(btnLayout)

    def _fetch(self):
        try:
            self.registros = self.sap.getCreditosQpt() or []
        except Exception:
            self.registros = []
        self.tabela.blockSignals(True)
        self.tabela.setRowCount(0)
        for r in self.registros:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [r.get('id'), r.get('nome'), r.get('qpt')]
            for col, v in enumerate(valores):
                self.tabela.setItem(row, col, QtWidgets.QTableWidgetItem('' if v is None else str(v)))
        self.tabela.resizeColumnsToContents()
        self.tabela.clearSelection()
        self.tabela.blockSignals(False)
        self._novo()

    def _onSelect(self):
        row = self.tabela.currentRow()
        if row < 0:
            return
        item = self.tabela.item(row, 0)
        if not item or not item.text():
            return
        self.currentId = int(item.text())
        self.nomeLe.setText(self.tabela.item(row, 1).text() if self.tabela.item(row, 1) else '')
        self.qptTe.setPlainText(self.tabela.item(row, 2).text() if self.tabela.item(row, 2) else '')

    def _novo(self):
        self.currentId = None
        self.tabela.clearSelection()
        self.nomeLe.clear()
        self.qptTe.clear()

    def _salvar(self):
        nome = self.nomeLe.text().strip()
        qpt = self.qptTe.toPlainText().strip()
        if not nome or not qpt:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Preencha o nome e o texto QPT.')
            return
        try:
            if self.currentId:
                data = {'id': self.currentId, 'nome': nome, 'qpt': qpt}
                message = self.sap.atualizaCreditosQpt([data])
            else:
                data = {'nome': nome, 'qpt': qpt}
                message = self.sap.criaCreditosQpt([data])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._fetch()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))

    def _remover(self):
        row = self.tabela.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um crédito na tabela.')
            return
        item = self.tabela.item(row, 0)
        if not item or not item.text():
            return
        if not QtWidgets.QMessageBox.question(self, 'Atenção', 'Remover o crédito selecionado?'):
            return
        try:
            message = self.sap.deletaCreditosQpt([int(item.text())])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._fetch()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
