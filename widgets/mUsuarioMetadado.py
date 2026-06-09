# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets


class MUsuarioMetadado(QtWidgets.QDialog):
    """Cadastro de metadado.usuario: o registro de pessoas (nome, funcao,
    organizacao) usado como responsavel nos metadados. Liga-se a um usuario do
    SAP (dgeo.usuario)."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(MUsuarioMetadado, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.usuariosSap = []
        self.organizacoes = []
        self.registros = []
        self.setWindowTitle('Usuários de Metadado')
        self.setMinimumWidth(640)
        self._loadAux()
        self._buildUi()
        self._fetch()

    def _loadAux(self):
        try:
            self.usuariosSap = self.sap.getUsers() or []
        except Exception:
            self.usuariosSap = []
        try:
            self.organizacoes = self.sap.getMetadadoOrganizacao() or []
        except Exception:
            self.organizacoes = []

    def _buildUi(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.tabela = QtWidgets.QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(['id', 'nome', 'função', 'organização'])
        self.tabela.setColumnHidden(0, True)
        self.tabela.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.tabela)

        form = QtWidgets.QFormLayout()
        self.usuarioSapCombo = QtWidgets.QComboBox()
        for u in self.usuariosSap:
            self.usuarioSapCombo.addItem(str(u.get('nome') or u.get('id')), u.get('id'))
        form.addRow('Usuário SAP:', self.usuarioSapCombo)
        self.nomeLe = QtWidgets.QLineEdit()
        form.addRow('Nome (metadado):', self.nomeLe)
        self.funcaoLe = QtWidgets.QLineEdit()
        form.addRow('Função:', self.funcaoLe)
        self.organizacaoCombo = QtWidgets.QComboBox()
        for o in self.organizacoes:
            self.organizacaoCombo.addItem(str(o.get('nome') or o.get('code')), o.get('code'))
        form.addRow('Organização:', self.organizacaoCombo)
        layout.addLayout(form)

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
        self.tabela.setRowCount(0)
        try:
            self.registros = self.sap.getMetadadoUsuarios() or []
        except Exception:
            self.registros = []
        for r in self.registros:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [r.get('id'), r.get('nome'), r.get('funcao'), r.get('organizacao')]
            for col, v in enumerate(valores):
                self.tabela.setItem(row, col, QtWidgets.QTableWidgetItem('' if v is None else str(v)))
        self.tabela.resizeColumnsToContents()

    def _adicionar(self):
        usuarioSapId = self.usuarioSapCombo.currentData()
        organizacaoId = self.organizacaoCombo.currentData()
        nome = self.nomeLe.text().strip()
        funcao = self.funcaoLe.text().strip()
        if usuarioSapId is None or organizacaoId is None or not nome or not funcao:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Preencha usuário, nome, função e organização.')
            return
        data = [{
            'usuario_sap_id': usuarioSapId,
            'nome': nome,
            'funcao': funcao,
            'organizacao_id': organizacaoId
        }]
        try:
            message = self.sap.criaMetadadoUsuarios(data)
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self.nomeLe.clear()
            self.funcaoLe.clear()
            self._fetch()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))

    def _remover(self):
        row = self.tabela.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um usuário na tabela.')
            return
        item = self.tabela.item(row, 0)
        if not item or not item.text():
            return
        if not QtWidgets.QMessageBox.question(self, 'Atenção', 'Remover o usuário selecionado?'):
            return
        try:
            message = self.sap.deletaMetadadoUsuarios([int(item.text())])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._fetch()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
