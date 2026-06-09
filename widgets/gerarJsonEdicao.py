# -*- coding: utf-8 -*-
import os, json
from qgis.PyQt import QtCore, QtWidgets
from SAP_Gerente.widgets.mMetadadoBase import MGerarLoteDialog


class GerarJsonEdicao(MGerarLoteDialog):
    """Gera, pelo backend do SAP, o JSON de edicao de todas as folhas de um lote
    (rota /metadados/json_edicao/lote/:loteId) e salva um arquivo por folha,
    nomeado pelo INOM/MI, na pasta escolhida. UTF-8 sem BOM."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(GerarJsonEdicao, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.setWindowTitle('Gerar JSON de Edição')
        self.setMinimumWidth(560)
        self._buildUi()
        self._loadLotes()

    def _buildUi(self):
        layout = QtWidgets.QVBoxLayout(self)

        formLayout = QtWidgets.QFormLayout()
        self.loteCombo = QtWidgets.QComboBox()
        formLayout.addRow('Lote:', self.loteCombo)

        pastaLayout = QtWidgets.QHBoxLayout()
        self.pastaLe = QtWidgets.QLineEdit()
        self.pastaLe.setReadOnly(True)
        self.pastaBtn = QtWidgets.QPushButton('Selecionar...')
        self.pastaBtn.clicked.connect(self._escolherPasta)
        pastaLayout.addWidget(self.pastaLe)
        pastaLayout.addWidget(self.pastaBtn)
        formLayout.addRow('Pasta de saída:', pastaLayout)
        layout.addLayout(formLayout)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addStretch()
        self.gerarBtn = QtWidgets.QPushButton('Gerar')
        self.gerarBtn.clicked.connect(self._gerar)
        self.fecharBtn = QtWidgets.QPushButton('Fechar')
        self.fecharBtn.clicked.connect(self.close)
        btnLayout.addWidget(self.gerarBtn)
        btnLayout.addWidget(self.fecharBtn)
        layout.addLayout(btnLayout)

    def _nomeArquivo(self, item):
        base = item.get('inom') or item.get('mi') or item.get('nome') or item.get('uuid')
        base = str(base).replace('/', '-').replace('\\', '-').strip()
        return base + '.json'

    def _gerar(self):
        loteId = self.loteCombo.currentData()
        pasta = self.pastaLe.text()
        if not loteId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um lote.')
            return
        if not pasta or not os.path.isdir(pasta):
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione uma pasta de saída válida.')
            return
        self.log.clear()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            itens = self.sap.getJsonEdicaoLote(loteId) or []
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
            return
        gravados, comErro = 0, 0
        for item in itens:
            label = item.get('inom') or item.get('mi') or item.get('nome') or item.get('uuid')
            erros = item.get('erros') or []
            jsonData = item.get('json')
            if not jsonData:
                comErro += 1
                self._appendLog('[ERRO] {0}: {1}'.format(label, '; '.join(erros) or 'sem JSON'))
                continue
            caminho = os.path.join(pasta, self._nomeArquivo(item))
            try:
                with open(caminho, 'w', encoding='utf-8') as f:
                    json.dump(jsonData, f, ensure_ascii=False, indent=2)
                gravados += 1
                if erros:
                    self._appendLog('[aviso] {0}: gravado com pendências: {1}'.format(label, '; '.join(erros)))
                else:
                    self._appendLog('[ok] {0}'.format(label))
            except Exception as e:
                comErro += 1
                self._appendLog('[ERRO] {0}: falha ao gravar: {1}'.format(label, e))
        QtWidgets.QApplication.restoreOverrideCursor()
        self._appendLog('\nConcluído: {0} gravado(s), {1} com erro/pendência crítica.'.format(gravados, comErro))
