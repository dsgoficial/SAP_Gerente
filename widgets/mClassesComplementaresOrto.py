# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from SAP_Gerente.widgets.mMetadadoBase import MMetadadoLoteAlvo
from SAP_Gerente.widgets.metadadoHelpers import (
    universoChecklist,
    resolveClassesListaId,
    PADRAO_DSG_FALLBACK,
)


class MClassesComplementaresOrto(MMetadadoLoteAlvo):
    """Seleciona as camadas opcionais (classes complementares) da carta
    ortoimagem por LOTE (recomendado) ou por PRODUTO, como um checklist em vez
    de JSON livre. Vem com o 'Padrao DSG' pre-marcado e permite adicionar do
    universo conhecido. Ao salvar, reusa a lista nomeada cujas classes batem
    com a selecao (ou cria uma nova) e grava o vinculo em
    metadado.perfil_classes_complementares_orto."""

    PADRAO_NOMES = ('Padrão DSG', 'Padrao DSG')

    def __init__(self, controller, qgis, sap, parent=None):
        super(MClassesComplementaresOrto, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.listas = []
        self.perfis = []
        self.padraoClasses = list(PADRAO_DSG_FALLBACK)
        self.currentPerfilId = None
        self.setWindowTitle('Classes Complementares da Carta Ortoimagem (camadas opcionais)')
        self.setMinimumWidth(560)
        self._buildUi()
        self._loadAux()
        self._loadLotes()

    def _buildUi(self):
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        self.loteCombo = QtWidgets.QComboBox()
        # listas e perfis sao globais (nao variam por lote): busca uma vez em
        # _loadAux e apos cada Salvar, nao a cada troca de lote.
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

        layout.addLayout(form)

        info = QtWidgets.QLabel(
            'Marque as camadas opcionais que entram na carta (além das obrigatórias). '
            'O conjunto "Padrão DSG" já vem marcado.'
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self.classesList = QtWidgets.QListWidget()
        self.classesList.setMinimumHeight(280)
        layout.addWidget(self.classesList)

        addLayout = QtWidgets.QHBoxLayout()
        self.novaClasseLe = QtWidgets.QLineEdit()
        self.novaClasseLe.setPlaceholderText('adicionar classe avulsa (ex.: edicao_limite_legal_l)')
        self.addClasseBtn = QtWidgets.QPushButton('Adicionar classe')
        self.addClasseBtn.clicked.connect(self._addCustomClasse)
        addLayout.addWidget(self.novaClasseLe)
        addLayout.addWidget(self.addClasseBtn)
        layout.addLayout(addLayout)

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addStretch()
        self.salvarBtn = QtWidgets.QPushButton('Salvar')
        self.salvarBtn.clicked.connect(self._salvar)
        self.fecharBtn = QtWidgets.QPushButton('Fechar')
        self.fecharBtn.clicked.connect(self.close)
        btnLayout.addWidget(self.salvarBtn)
        btnLayout.addWidget(self.fecharBtn)
        layout.addLayout(btnLayout)

    def _loadAux(self):
        self._refreshDados()

    def _refreshDados(self):
        try:
            self.listas = self.sap.getClassesComplementaresOrto() or []
        except Exception:
            self.listas = []
        try:
            self.perfis = self.sap.getPerfilClassesComplementaresOrto() or []
        except Exception:
            self.perfis = []
        for lst in self.listas:
            if str(lst.get('nome') or '').strip() in self.PADRAO_NOMES:
                self.padraoClasses = list(lst.get('classes') or [])
                break

    def _findPerfil(self, destino, alvoId):
        chave = 'produto_id' if destino == 'produto' else 'lote_id'
        for p in self.perfis:
            if p.get(chave) == alvoId:
                return p
        return None

    def _checkedClasses(self):
        selecionadas = []
        for i in range(self.classesList.count()):
            item = self.classesList.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selecionadas.append(item.text())
        return selecionadas

    def _populateChecklist(self, selected):
        selectedSet = set(selected or [])
        self.classesList.clear()
        for classe in universoChecklist(selected, self.listas):
            item = QtWidgets.QListWidgetItem(classe)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if classe in selectedSet else Qt.CheckState.Unchecked
            )
            self.classesList.addItem(item)

    def _prefill(self):
        alvoId = self.alvoCombo.currentData()
        perfil = self._findPerfil(self._destino(), alvoId) if alvoId else None
        if perfil:
            self.currentPerfilId = perfil.get('id')
            selected = perfil.get('classes') or []
        else:
            self.currentPerfilId = None
            selected = list(self.padraoClasses)
        self._populateChecklist(selected)

    def _addCustomClasse(self):
        nome = self.novaClasseLe.text().strip()
        if not nome:
            return
        if ' ' in nome:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Nome de classe inválido (sem espaços).')
            return
        for i in range(self.classesList.count()):
            if self.classesList.item(i).text() == nome:
                self.classesList.item(i).setCheckState(Qt.CheckState.Checked)
                self.novaClasseLe.clear()
                return
        item = QtWidgets.QListWidgetItem(nome)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        self.classesList.insertItem(0, item)
        self.novaClasseLe.clear()

    def _salvar(self):
        alvoId = self.alvoCombo.currentData()
        if not alvoId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um alvo (lote ou produto).')
            return

        chosen = sorted(set(self._checkedClasses()))

        # Sem classes opcionais: remove o vinculo existente (carta so com as
        # obrigatorias) em vez de gravar uma lista vazia.
        if not chosen:
            if self.currentPerfilId:
                try:
                    msg = self.sap.deletaPerfilClassesComplementaresOrto([self.currentPerfilId])
                    if msg:
                        QtWidgets.QMessageBox.information(self, 'Aviso', msg)
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
                    return
            else:
                QtWidgets.QMessageBox.information(self, 'Aviso', 'Nenhuma classe selecionada.')
            # Mostra o estado limpo (so obrigatorias) em vez de reabrir com o
            # Padrao DSG pre-marcado: sem perfil, _prefill re-marcaria o padrao e
            # um segundo Salvar recriaria silenciosamente o vinculo recem-removido.
            self.currentPerfilId = None
            self._refreshDados()
            self._populateChecklist([])
            return

        listaId = resolveClassesListaId(chosen, self.listas)
        if listaId is None:
            nome = 'Custom - {0}'.format(self.alvoCombo.currentText())[:255]
            try:
                self.sap.criaClassesComplementaresOrto([{'nome': nome, 'classes': chosen}])
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
                return
            self._refreshDados()
            listaId = resolveClassesListaId(chosen, self.listas)
            if listaId is None:
                QtWidgets.QMessageBox.critical(
                    self, 'Erro', 'Não foi possível recuperar a lista de classes criada.'
                )
                return

        payload = {'classes_complementares_orto_id': listaId}
        if self._destino() == 'produto':
            payload['produto_id'] = alvoId
        else:
            payload['lote_id'] = alvoId

        try:
            if self.currentPerfilId:
                payload['id'] = self.currentPerfilId
                msg = self.sap.atualizaPerfilClassesComplementaresOrto([payload])
            else:
                msg = self.sap.criaPerfilClassesComplementaresOrto([payload])
            if msg:
                QtWidgets.QMessageBox.information(self, 'Aviso', msg)
            self._refreshDados()
            self._prefill()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
