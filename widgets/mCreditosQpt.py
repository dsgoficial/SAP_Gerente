# -*- coding: utf-8 -*-
import os

from qgis.PyQt import QtWidgets


class MCreditosQpt(QtWidgets.QDialog):
    """Cadastro dos creditos QPT (metadado.creditos_qpt), consumidos pela tela
    de Metadados de Edicao da Carta. Tabela global (id, nome, qpt): nao e por
    lote nem por produto. Selecionar uma linha carrega no formulario para
    edicao; o botao Salvar cria (sem selecao) ou atualiza (com selecao).

    O conteudo QPT e carregado a partir de um arquivo .qpt (template de layout
    do QGIS, XML UTF-8). Na edicao, se nenhum arquivo novo for selecionado, o
    QPT atual do registro e mantido."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(MCreditosQpt, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.registros = []
        self.currentId = None
        self.qptContent = None  # conteudo QPT em memoria (registro ou arquivo novo)
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

        arquivoLayout = QtWidgets.QHBoxLayout()
        self.arquivoLe = QtWidgets.QLineEdit()
        self.arquivoLe.setReadOnly(True)
        self.arquivoLe.setPlaceholderText('selecione um arquivo .qpt')
        self.selecionarBtn = QtWidgets.QPushButton('Selecionar .qpt')
        self.selecionarBtn.clicked.connect(self._selecionarArquivo)
        arquivoLayout.addWidget(self.arquivoLe)
        arquivoLayout.addWidget(self.selecionarBtn)
        form.addRow('Arquivo QPT:', arquivoLayout)

        self.statusLb = QtWidgets.QLabel('Nenhum QPT carregado')
        form.addRow('', self.statusLb)
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

    def _qptResumo(self, qpt):
        """Resumo leve do QPT para nao renderizar o XML inteiro (pode ter MBs)."""
        if not qpt:
            return ''
        return '{} caracteres'.format(len(qpt))

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
            valores = [r.get('id'), r.get('nome'), self._qptResumo(r.get('qpt'))]
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
        registro = next((r for r in self.registros if r.get('id') == self.currentId), None)
        self.nomeLe.setText(registro.get('nome') if registro else '')
        self.qptContent = registro.get('qpt') if registro else None
        self.arquivoLe.clear()
        if self.qptContent:
            self.statusLb.setText('QPT atual: {}'.format(self._qptResumo(self.qptContent)))
        else:
            self.statusLb.setText('Nenhum QPT carregado')

    def _novo(self):
        self.currentId = None
        self.qptContent = None
        self.tabela.clearSelection()
        self.nomeLe.clear()
        self.arquivoLe.clear()
        self.statusLb.setText('Nenhum QPT carregado')

    def _selecionarArquivo(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Selecionar arquivo QPT', '', '*.qpt')[0]
        if not filePath:
            return
        try:
            with open(filePath, 'r', encoding='utf-8') as f:
                self.qptContent = f.read()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Não foi possível ler o arquivo: {}'.format(str(e)))
            return
        self.arquivoLe.setText(filePath)
        self.statusLb.setText('Novo arquivo: {} ({})'.format(
            os.path.basename(filePath), self._qptResumo(self.qptContent)))

    def _salvar(self):
        nome = self.nomeLe.text().strip()
        qpt = self.qptContent
        if not nome:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Preencha o nome.')
            return
        if not qpt:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um arquivo .qpt.')
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
