# -*- coding: utf-8 -*-
from qgis.PyQt import QtCore, QtWidgets


class MOrganizacao(QtWidgets.QDialog):
    """Edita o contato das organizacoes (CGEO) usado no XML de metadados como
    produtor/distribuidor: nome, sigla, endereco, telefone e site. Permite a
    qualquer CGEO definir o seu orgao. O gerador usa a organizacao responsavel do
    produto (escolhida em Informacoes do Produto) para preencher organisationName,
    telefone, endereco e o site (CI_OnlineResource) do XML."""

    COLS = [('code', 'code'), ('nome', 'nome'), ('sigla', 'sigla'),
            ('endereco', 'endereço'), ('telefone', 'telefone'), ('site', 'site')]

    def __init__(self, controller, qgis, sap, parent=None):
        super(MOrganizacao, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.registros = []
        self.setWindowTitle('Organizações (produtor/distribuidor dos metadados)')
        self.setMinimumWidth(820)
        self._buildUi()
        self._fetch()

    def _buildUi(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel(
            'Edite o contato de cada órgão e clique em Salvar. Esses dados preenchem '
            'organisationName, telefone, endereço e site (CI_OnlineResource) no XML de metadados.'))
        self.tabela = QtWidgets.QTableWidget(0, len(self.COLS))
        self.tabela.setHorizontalHeaderLabels([c[1] for c in self.COLS])
        self.tabela.setColumnHidden(0, True)  # code (oculto, nao editavel)
        self.tabela.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.tabela)

        btnLayout = QtWidgets.QHBoxLayout()
        self.salvarBtn = QtWidgets.QPushButton('Salvar')
        self.salvarBtn.clicked.connect(self._salvar)
        btnLayout.addWidget(self.salvarBtn)
        btnLayout.addStretch()
        self.fecharBtn = QtWidgets.QPushButton('Fechar')
        self.fecharBtn.clicked.connect(self.close)
        btnLayout.addWidget(self.fecharBtn)
        layout.addLayout(btnLayout)

    def _fetch(self):
        self.tabela.setRowCount(0)
        try:
            self.registros = self.sap.getMetadadoOrganizacao() or []
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
            self.registros = []
        for r in self.registros:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col, (key, _) in enumerate(self.COLS):
                v = r.get(key)
                item = QtWidgets.QTableWidgetItem('' if v is None else str(v))
                if key == 'code':
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, col, item)
        self.tabela.resizeColumnsToContents()

    def _salvar(self):
        organizacoes = []
        for row in range(self.tabela.rowCount()):
            reg = {}
            for col, (key, _) in enumerate(self.COLS):
                cell = self.tabela.item(row, col)
                txt = cell.text().strip() if cell else ''
                if key == 'code':
                    reg[key] = int(txt)
                elif key == 'nome':
                    reg[key] = txt
                else:
                    reg[key] = txt or None
            if not reg.get('nome'):
                QtWidgets.QMessageBox.warning(self, 'Aviso', 'O nome do órgão é obrigatório.')
                return
            organizacoes.append(reg)
        if not organizacoes:
            return
        try:
            message = self.sap.atualizaMetadadoOrganizacao(organizacoes)
            QtWidgets.QMessageBox.information(self, 'Aviso', message or 'Organizações salvas.')
            self._fetch()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
