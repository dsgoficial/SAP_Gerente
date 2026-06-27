# -*- coding: utf-8 -*-
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from SAP_Gerente.widgets.mMetadadoBase import MMetadadoLoteAlvo
from SAP_Gerente.widgets.metadadoHelpers import (
    quadroFasesFromDict,
    quadroFasesToDict,
    cleanStringList,
)


def _commitInlineEditor(widget):
    """Confirma um editor inline aberto (editItem) dentro de `widget` antes de
    ler seus valores. Sem isso, um Salvar com edicao em andamento (sem Enter nem
    troca de foco) leria o texto antigo e descartaria o que foi digitado: tirar o
    foco do editor dispara o commit do delegate (FocusOut)."""
    fw = QtWidgets.QApplication.focusWidget()
    if fw is not None and widget.isAncestorOf(fw):
        fw.clearFocus()


class QuadroFasesEditor(QtWidgets.QWidget):
    """Editor estruturado do quadro de fases (substitui o JSON livre): arvore de
    fases (nivel raiz, nome editavel) com executantes como filhos (nome, ano)."""

    def __init__(self, parent=None):
        super(QuadroFasesEditor, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['Fase / Executante', 'Ano'])
        self.tree.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked
            | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked
        )
        self.tree.setFixedHeight(160)
        layout.addWidget(self.tree)

        btns = QtWidgets.QHBoxLayout()
        self.addFaseBtn = QtWidgets.QPushButton('Adicionar fase')
        self.addFaseBtn.clicked.connect(self._addFase)
        self.addExecBtn = QtWidgets.QPushButton('Adicionar executante')
        self.addExecBtn.clicked.connect(self._addExecutante)
        self.removeBtn = QtWidgets.QPushButton('Remover')
        self.removeBtn.clicked.connect(self._remove)
        btns.addWidget(self.addFaseBtn)
        btns.addWidget(self.addExecBtn)
        btns.addWidget(self.removeBtn)
        btns.addStretch()
        layout.addLayout(btns)

    def _novaFase(self, nome=''):
        item = QtWidgets.QTreeWidgetItem([nome, ''])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.tree.addTopLevelItem(item)
        item.setExpanded(True)
        return item

    def _novoExecutante(self, faseItem, nome='', ano=''):
        child = QtWidgets.QTreeWidgetItem([nome, ano])
        child.setFlags(child.flags() | Qt.ItemFlag.ItemIsEditable)
        faseItem.addChild(child)
        faseItem.setExpanded(True)
        return child

    def _faseSelecionada(self):
        item = self.tree.currentItem()
        if item is None:
            return None
        return item.parent() if item.parent() is not None else item

    def _addFase(self):
        item = self._novaFase()
        self.tree.setCurrentItem(item)
        self.tree.editItem(item, 0)

    def _addExecutante(self):
        fase = self._faseSelecionada()
        if fase is None:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione (ou crie) uma fase primeiro.')
            return
        child = self._novoExecutante(fase)
        self.tree.setCurrentItem(child)
        self.tree.editItem(child, 0)

    def _remove(self):
        item = self.tree.currentItem()
        if item is None:
            return
        parent = item.parent()
        if parent is not None:
            parent.removeChild(item)
        else:
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))

    def clear(self):
        self.tree.clear()

    def setFases(self, fases):
        self.tree.clear()
        for fase in (fases or []):
            faseItem = self._novaFase(fase.get('nome', ''))
            for ex in (fase.get('executantes') or []):
                self._novoExecutante(faseItem, ex.get('nome', ''), ex.get('ano', ''))

    def fases(self):
        out = []
        for i in range(self.tree.topLevelItemCount()):
            faseItem = self.tree.topLevelItem(i)
            executantes = [
                {'nome': faseItem.child(j).text(0), 'ano': faseItem.child(j).text(1)}
                for j in range(faseItem.childCount())
            ]
            out.append({'nome': faseItem.text(0), 'executantes': executantes})
        return out


class StringListEditor(QtWidgets.QWidget):
    """Editor de lista de strings (substitui o textarea linha-a-linha): cada item
    e uma linha editavel, com botoes Adicionar/Remover. items() devolve as
    strings nao vazias, na ordem (sem o split silencioso por linha)."""

    def __init__(self, dica='', addLabel='Adicionar', parent=None):
        super(StringListEditor, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lista = QtWidgets.QListWidget()
        self.lista.setFixedHeight(80)
        if dica:
            self.lista.setToolTip(dica)
        layout.addWidget(self.lista)

        btns = QtWidgets.QHBoxLayout()
        self.addBtn = QtWidgets.QPushButton(addLabel)
        self.addBtn.clicked.connect(self._add)
        self.removeBtn = QtWidgets.QPushButton('Remover')
        self.removeBtn.clicked.connect(self._remove)
        btns.addWidget(self.addBtn)
        btns.addWidget(self.removeBtn)
        btns.addStretch()
        layout.addLayout(btns)

    def _novoItem(self, texto=''):
        item = QtWidgets.QListWidgetItem(texto)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.lista.addItem(item)
        return item

    def _add(self):
        item = self._novoItem('')
        self.lista.setCurrentItem(item)
        self.lista.editItem(item)

    def _remove(self):
        row = self.lista.currentRow()
        if row >= 0:
            self.lista.takeItem(row)

    def clear(self):
        self.lista.clear()

    def setItems(self, valores):
        self.lista.clear()
        for v in (valores or []):
            self._novoItem(str(v))

    def items(self):
        return cleanStringList(
            self.lista.item(i).text() for i in range(self.lista.count())
        )


class MInfoEdicao(MMetadadoLoteAlvo):
    """Preenche metadado.informacoes_edicao por LOTE (conjunto homogeneo de
    folhas: mesma escala e linha de producao, recomendado) ou por PRODUTO
    (excecao). E a fonte do bloco info_tecnica + MDE + fases + licenca do JSON
    de edicao. Formulario upsert: se o alvo ja tem registro, prefilla e atualiza;
    senao, cria."""

    LICENCAS = ['', 'CC-BY-SA 4.0', 'CC-BY-NC-SA 4.0']

    def __init__(self, controller, qgis, sap, parent=None):
        super(MInfoEdicao, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.creditos = []
        self.registros = []
        self.currentId = None
        self.setWindowTitle('Metadados de Edição da Carta (por lote ou produto)')
        self.setMinimumWidth(640)
        self._buildUi()
        self._loadAux()
        self._loadLotes()

    def _buildUi(self):
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        self.loteCombo = QtWidgets.QComboBox()
        # refresh dos registros antes de repovoar o alvo (a ordem dos connects
        # garante que o _prefill, disparado pelo alvoCombo, use dados atualizados)
        self.loteCombo.currentIndexChanged.connect(self._refreshRegistros)
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

        self.pecPlanimetricoLe = QtWidgets.QLineEdit()
        form.addRow('PEC planimétrico:', self.pecPlanimetricoLe)
        self.pecAltimetricoLe = QtWidgets.QLineEdit()
        form.addRow('PEC altimétrico:', self.pecAltimetricoLe)
        self.origemLe = QtWidgets.QLineEdit()
        form.addRow('Origem dados altimétricos:', self.origemLe)
        self.dataCriacaoLe = QtWidgets.QLineEdit()
        self.dataCriacaoLe.setPlaceholderText('DD/MM/AAAA')
        form.addRow('Data de criação:', self.dataCriacaoLe)

        self.epsgMdeLe = QtWidgets.QLineEdit()
        form.addRow('EPSG do MDE:', self.epsgMdeLe)
        self.caminhoMdeLe = QtWidgets.QLineEdit()
        self.caminhoMdeLe.setPlaceholderText('caminho absoluto, sem espaços')
        form.addRow('Caminho do MDE:', self.caminhoMdeLe)

        self.creditosCombo = QtWidgets.QComboBox()
        form.addRow('Créditos (QPT):', self.creditosCombo)

        self.dadosTerceiroEditor = StringListEditor(
            dica='um crédito de terceiro por item', addLabel='Adicionar crédito'
        )
        form.addRow('Dados de terceiros:', self.dadosTerceiroEditor)

        self.quadroFasesEditor = QuadroFasesEditor()
        form.addRow('Quadro de fases:', self.quadroFasesEditor)

        self.tipoProdutoLe = QtWidgets.QLineEdit()
        self.tipoProdutoLe.setPlaceholderText('ex.: Carta Topográfica (vazio = derivado)')
        form.addRow('tipo_produto (plugin):', self.tipoProdutoLe)
        self.versaoProdutoLe = QtWidgets.QLineEdit()
        self.versaoProdutoLe.setPlaceholderText('ex.: 2.0 / 3.0 (vazio = derivado)')
        form.addRow('versao_produto (plugin):', self.versaoProdutoLe)

        self.licencaCombo = QtWidgets.QComboBox()
        self.licencaCombo.addItems(self.LICENCAS)
        form.addRow('Licença (vazio = contaminação):', self.licencaCombo)

        self.observacoesEditor = StringListEditor(
            dica='uma observação (asterisco) por item', addLabel='Adicionar observação'
        )
        form.addRow('Observações:', self.observacoesEditor)

        self.dpiSpin = QtWidgets.QSpinBox()
        self.dpiSpin.setRange(72, 1200)
        self.dpiSpin.setValue(300)
        form.addRow('DPI:', self.dpiSpin)

        self.territorioCb = QtWidgets.QCheckBox('Território internacional')
        self.acessoRestritoCb = QtWidgets.QCheckBox('Acesso restrito')
        self.cartaMilitarCb = QtWidgets.QCheckBox('Carta militar')
        flags = QtWidgets.QHBoxLayout()
        flags.addWidget(self.territorioCb)
        flags.addWidget(self.acessoRestritoCb)
        flags.addWidget(self.cartaMilitarCb)
        form.addRow('Flags:', flags)

        layout.addLayout(form)

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
        try:
            self.creditos = self.sap.getCreditosQpt() or []
        except Exception:
            self.creditos = []
        self.creditosCombo.clear()
        self.creditosCombo.addItem('(sem crédito)', None)
        for c in self.creditos:
            self.creditosCombo.addItem(c.get('nome', str(c.get('id'))), c.get('id'))
        self._refreshRegistros()

    def _refreshRegistros(self):
        try:
            self.registros = self.sap.getInformacoesEdicao() or []
        except Exception:
            self.registros = []

    def _findRegistro(self, destino, alvoId):
        chave = 'produto_id' if destino == 'produto' else 'lote_id'
        for r in self.registros:
            if r.get(chave) == alvoId:
                return r
        return None

    def _clearForm(self):
        """Reseta o formulario para o estado de novo cadastro."""
        self.currentId = None
        self.salvarBtn.setText('Salvar')
        self.pecPlanimetricoLe.clear()
        self.pecAltimetricoLe.clear()
        self.origemLe.clear()
        self.dataCriacaoLe.clear()
        self.epsgMdeLe.clear()
        self.caminhoMdeLe.clear()
        self.creditosCombo.setCurrentIndex(0)
        self.dadosTerceiroEditor.clear()
        self.quadroFasesEditor.clear()
        self.tipoProdutoLe.clear()
        self.versaoProdutoLe.clear()
        self.licencaCombo.setCurrentIndex(0)
        self.observacoesEditor.clear()
        self.dpiSpin.setValue(300)
        self.territorioCb.setChecked(False)
        self.acessoRestritoCb.setChecked(False)
        self.cartaMilitarCb.setChecked(False)

    def _prefill(self):
        alvoId = self.alvoCombo.currentData()
        r = self._findRegistro(self._destino(), alvoId) if alvoId else None
        if not r:
            self._clearForm()
            return
        self.currentId = r.get('id')
        self.salvarBtn.setText('Atualizar')
        self.pecPlanimetricoLe.setText(str(r.get('pec_planimetrico') or ''))
        self.pecAltimetricoLe.setText(str(r.get('pec_altimetrico') or ''))
        self.origemLe.setText(str(r.get('origem_dados_altimetricos') or ''))
        self.dataCriacaoLe.setText(str(r.get('data_criacao') or ''))
        self.epsgMdeLe.setText(str(r.get('epsg_mde') or ''))
        self.caminhoMdeLe.setText(str(r.get('caminho_mde') or ''))
        idx = self.creditosCombo.findData(r.get('creditos_id'))
        self.creditosCombo.setCurrentIndex(idx if idx >= 0 else 0)
        self.dadosTerceiroEditor.setItems(r.get('dados_terceiro') or [])
        self.quadroFasesEditor.setFases(quadroFasesFromDict(r.get('quadro_fases')))
        self.tipoProdutoLe.setText(str(r.get('tipo_produto') or ''))
        self.versaoProdutoLe.setText(str(r.get('versao_produto') or ''))
        licIdx = self.licencaCombo.findText(str(r.get('licenca_produto') or ''))
        self.licencaCombo.setCurrentIndex(licIdx if licIdx >= 0 else 0)
        self.observacoesEditor.setItems(r.get('observacoes') or [])
        self.dpiSpin.setValue(int(r.get('dpi') or 300))
        self.territorioCb.setChecked(bool(r.get('territorio_internacional')))
        self.acessoRestritoCb.setChecked(bool(r.get('acesso_restrito')))
        self.cartaMilitarCb.setChecked(bool(r.get('carta_militar')))

    def _salvar(self):
        alvoId = self.alvoCombo.currentData()
        if not alvoId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um alvo (lote ou produto).')
            return
        # confirma edicoes inline em andamento antes de ler os editores
        _commitInlineEditor(self.dadosTerceiroEditor)
        _commitInlineEditor(self.quadroFasesEditor)
        _commitInlineEditor(self.observacoesEditor)

        creditosId = self.creditosCombo.currentData()
        quadroFases = quadroFasesToDict(self.quadroFasesEditor.fases())

        licenca = self.licencaCombo.currentText().strip()

        data = {
            'pec_planimetrico': self.pecPlanimetricoLe.text().strip(),
            'pec_altimetrico': self.pecAltimetricoLe.text().strip(),
            'origem_dados_altimetricos': self.origemLe.text().strip(),
            'territorio_internacional': self.territorioCb.isChecked(),
            'acesso_restrito': self.acessoRestritoCb.isChecked(),
            'carta_militar': self.cartaMilitarCb.isChecked(),
            'data_criacao': self.dataCriacaoLe.text().strip(),
            'creditos_id': creditosId,
            'epsg_mde': self.epsgMdeLe.text().strip(),
            'caminho_mde': self.caminhoMdeLe.text().strip(),
            'dados_terceiro': self.dadosTerceiroEditor.items(),
            'quadro_fases': quadroFases,
            'tipo_produto': self.tipoProdutoLe.text().strip() or None,
            'versao_produto': self.versaoProdutoLe.text().strip() or None,
            'licenca_produto': licenca or None,
            'observacoes': self.observacoesEditor.items() or None,
            'dpi': self.dpiSpin.value()
        }
        if self._destino() == 'produto':
            data['produto_id'] = alvoId
        else:
            data['lote_id'] = alvoId
        try:
            if self.currentId:
                data['id'] = self.currentId
                message = self.sap.atualizaInformacoesEdicao([data])
            else:
                message = self.sap.criaInformacoesEdicao([data])
            if message:
                QtWidgets.QMessageBox.information(self, 'Aviso', message)
            self._loadAux()
            self._prefill()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
