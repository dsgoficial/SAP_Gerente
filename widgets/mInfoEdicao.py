# -*- coding: utf-8 -*-
import json
from qgis.PyQt import QtWidgets
from SAP_Gerente.widgets.mMetadadoBase import MMetadadoLoteAlvo


class MInfoEdicao(MMetadadoLoteAlvo):
    """Preenche metadado.informacoes_edicao por LOTE (conjunto homogeneo de
    folhas: mesma escala e linha de producao, recomendado) ou por PRODUTO
    (excecao). E a fonte do bloco info_tecnica + MDE + fases + licenca do JSON
    de edicao. Formulario upsert: se o alvo ja tem registro, prefilla e atualiza;
    senao, cria."""

    LICENCAS = ['', 'CC-BY-SA 4.0', 'CC-BY-NC-SA 4.0']

    QUADRO_FASES_EXEMPLO = (
        '{\n'
        '  "fases": [\n'
        '    {"nome": "Edição", "executantes": [{"nome": "Fulano", "ano": "2025"}]}\n'
        '  ]\n'
        '}'
    )

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
        self.loteCombo.currentIndexChanged.connect(self._loadAlvos)
        form.addRow('Lote:', self.loteCombo)

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

        self.dadosTerceiroTe = QtWidgets.QPlainTextEdit()
        self.dadosTerceiroTe.setPlaceholderText('um crédito de terceiro por linha')
        self.dadosTerceiroTe.setFixedHeight(60)
        form.addRow('Dados de terceiros:', self.dadosTerceiroTe)

        self.quadroFasesTe = QtWidgets.QPlainTextEdit()
        self.quadroFasesTe.setPlainText(self.QUADRO_FASES_EXEMPLO)
        self.quadroFasesTe.setFixedHeight(120)
        form.addRow('Quadro de fases (JSON):', self.quadroFasesTe)

        self.tipoProdutoLe = QtWidgets.QLineEdit()
        self.tipoProdutoLe.setPlaceholderText('ex.: Carta Topográfica (vazio = derivado)')
        form.addRow('tipo_produto (plugin):', self.tipoProdutoLe)
        self.versaoProdutoLe = QtWidgets.QLineEdit()
        self.versaoProdutoLe.setPlaceholderText('ex.: 2.0 / 3.0 (vazio = derivado)')
        form.addRow('versao_produto (plugin):', self.versaoProdutoLe)

        self.licencaCombo = QtWidgets.QComboBox()
        self.licencaCombo.addItems(self.LICENCAS)
        form.addRow('Licença (vazio = contaminação):', self.licencaCombo)

        self.observacoesTe = QtWidgets.QPlainTextEdit()
        self.observacoesTe.setPlaceholderText('uma observação (asterisco) por linha')
        self.observacoesTe.setFixedHeight(60)
        form.addRow('Observações:', self.observacoesTe)

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
        for c in self.creditos:
            self.creditosCombo.addItem(c.get('nome', str(c.get('id'))), c.get('id'))
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

    def _prefill(self):
        alvoId = self.alvoCombo.currentData()
        self.currentId = None
        if not alvoId:
            return
        r = self._findRegistro(self._destino(), alvoId)
        if not r:
            return
        self.currentId = r.get('id')
        self.pecPlanimetricoLe.setText(str(r.get('pec_planimetrico') or ''))
        self.pecAltimetricoLe.setText(str(r.get('pec_altimetrico') or ''))
        self.origemLe.setText(str(r.get('origem_dados_altimetricos') or ''))
        self.dataCriacaoLe.setText(str(r.get('data_criacao') or ''))
        self.epsgMdeLe.setText(str(r.get('epsg_mde') or ''))
        self.caminhoMdeLe.setText(str(r.get('caminho_mde') or ''))
        idx = self.creditosCombo.findData(r.get('creditos_id'))
        if idx >= 0:
            self.creditosCombo.setCurrentIndex(idx)
        self.dadosTerceiroTe.setPlainText('\n'.join(r.get('dados_terceiro') or []))
        qf = r.get('quadro_fases')
        if qf is not None:
            self.quadroFasesTe.setPlainText(json.dumps(qf, ensure_ascii=False, indent=2))
        self.tipoProdutoLe.setText(str(r.get('tipo_produto') or ''))
        self.versaoProdutoLe.setText(str(r.get('versao_produto') or ''))
        licIdx = self.licencaCombo.findText(str(r.get('licenca_produto') or ''))
        self.licencaCombo.setCurrentIndex(licIdx if licIdx >= 0 else 0)
        self.observacoesTe.setPlainText('\n'.join(r.get('observacoes') or []))
        self.dpiSpin.setValue(int(r.get('dpi') or 300))
        self.territorioCb.setChecked(bool(r.get('territorio_internacional')))
        self.acessoRestritoCb.setChecked(bool(r.get('acesso_restrito')))
        self.cartaMilitarCb.setChecked(bool(r.get('carta_militar')))

    def _linhas(self, textEdit):
        return [linha.strip() for linha in textEdit.toPlainText().splitlines() if linha.strip()]

    def _salvar(self):
        alvoId = self.alvoCombo.currentData()
        if not alvoId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um alvo (lote ou produto).')
            return
        creditosId = self.creditosCombo.currentData()
        if creditosId is None:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Cadastre/escolha um crédito QPT.')
            return
        try:
            quadroFases = json.loads(self.quadroFasesTe.toPlainText())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Quadro de fases não é um JSON válido: {0}'.format(e))
            return
        if isinstance(quadroFases, list):
            quadroFases = {'fases': quadroFases}

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
            'dados_terceiro': self._linhas(self.dadosTerceiroTe),
            'quadro_fases': quadroFases,
            'tipo_produto': self.tipoProdutoLe.text().strip() or None,
            'versao_produto': self.versaoProdutoLe.text().strip() or None,
            'licenca_produto': licenca or None,
            'observacoes': self._linhas(self.observacoesTe) or None,
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
