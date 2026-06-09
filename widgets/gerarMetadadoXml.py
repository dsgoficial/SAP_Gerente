# -*- coding: utf-8 -*-
import os
from qgis.PyQt import QtCore, QtWidgets
from SAP_Gerente.widgets.mMetadadoBase import MGerarLoteDialog


class GerarMetadadoXml(MGerarLoteDialog):
    """Gera, pelo backend do SAP, o XML de metadados (Perfil MGB / ISO 19115) de
    cada produto de um lote: uma carta OU um vetor por produto, conforme o
    tipo_produto (o CDGV vetorial e um produto separado, com uuid proprio). O
    fileIdentifier = uuid do produto e o bounding box ja vem preenchido. Salva na
    pasta escolhida, UTF-8 sem BOM; o vetor sai com sufixo _vetor."""

    def __init__(self, controller, qgis, sap, parent=None):
        super(GerarMetadadoXml, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.setWindowTitle('Gerar Metadados XML')
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

    def _base(self, item):
        base = item.get('mi') or item.get('inom') or item.get('nome') or item.get('uuid')
        return str(base).replace('/', '-').replace('\\', '-').strip()

    def _gravar(self, registro, caminho, label):
        erros = (registro or {}).get('erros') or []
        xml = (registro or {}).get('xml')
        if not xml:
            self._appendLog('[ERRO] {0}: {1}'.format(label, '; '.join(erros) or 'sem XML'))
            return 0, 1
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(xml)
        except Exception as e:
            self._appendLog('[ERRO] {0}: falha ao gravar: {1}'.format(label, e))
            return 0, 1
        if erros:
            self._appendLog('[aviso] {0}: gravado com pendências: {1}'.format(label, '; '.join(erros)))
        else:
            self._appendLog('[ok] {0}'.format(label))
        return 1, 0

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
            itens = self.sap.getMetadadoXmlLote(loteId) or []
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
            return
        gravados, comErro = 0, 0
        for item in itens:
            base = self._base(item)
            sufixo = '_vetor' if item.get('kind') == 'vetor' else ''
            rotulo = '{0} ({1})'.format(base, item.get('kind') or '?')
            g, e = self._gravar(item, os.path.join(pasta, base + sufixo + '.xml'), rotulo)
            gravados += g
            comErro += e
        QtWidgets.QApplication.restoreOverrideCursor()
        self._appendLog('\nConcluído: {0} gravado(s), {1} com erro/pendência crítica.'.format(gravados, comErro))
