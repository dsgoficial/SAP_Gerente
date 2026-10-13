# -*- coding: utf-8 -*-
"""Classes-base dos widgets de metadado/JSON/XML do SAP Gerente.

Concentram o que era repetido em cada widget: o carregamento de lotes, o
seletor Lote/Produto (destino + alvo) e os utilitarios dos widgets de geracao
(escolher pasta, log). Os widgets concretos so criam os combos com os nomes
esperados (loteCombo, destinoCombo, alvoCombo, pastaLe, log) e implementam a
parte especifica.
"""
from qgis.PyQt import QtWidgets
from SAP_Gerente.modules.sap.api.contrato import emAndamento, STATUS_ENCERRADO


class MLoteComboDialog(QtWidgets.QDialog):
    """Base com o carregamento do combo de lotes (usado por todos)."""

    def _loadLotes(self):
        try:
            lotes = self.sap.getAllLots() or []
        except Exception:
            lotes = []
        # Se o widget tiver um checkbox 'Mostrar lotes finalizados' e ele estiver
        # desmarcado, exibe apenas lotes não encerrados (SAP 3.0).
        checkbox = getattr(self, 'showFinishedCheckBox', None)
        if checkbox is not None and not checkbox.isChecked():
            lotes = [lote for lote in lotes if emAndamento(lote)]
        self.loteCombo.clear()
        for lote in lotes:
            nome = lote.get('nome') or str(lote.get('id'))
            self.loteCombo.addItem(nome, lote.get('id'))


class MMetadadoLoteAlvo(MLoteComboDialog):
    """Base dos widgets de preenchimento de metadado: seletor Lote (recomendado)
    ou Versao (excecao; no SAP 3.0 o alvo e `versao_id`). O widget cria loteCombo/destinoCombo/alvoCombo e liga
    os sinais; aqui ficam a leitura do destino e a populacao do alvo."""

    def _destino(self):
        return self.destinoCombo.currentData()

    def _loadAlvos(self):
        loteId = self.loteCombo.currentData()
        self.alvoCombo.clear()
        if not loteId:
            return
        if self._destino() == 'lote':
            self.alvoCombo.addItem(self.loteCombo.currentText(), loteId)
        else:
            try:
                produtos = self.sap.getProdutosDoLote(loteId) or []
            except Exception as e:
                # SAP 3.0: não há rota que liste as versões do lote com o id;
                # a mensagem diz isso, e o destino volta para o lote.
                QtWidgets.QMessageBox.warning(self, 'Aviso', str(e))
                self.destinoCombo.setCurrentIndex(self.destinoCombo.findData('lote'))
                return
            for p in produtos:
                label = p.get('inom') or p.get('mi') or p.get('nome') or str(p.get('id'))
                self.alvoCombo.addItem(str(label), p.get('id'))


class MGerarLoteDialog(MLoteComboDialog):
    """Base dos widgets de geracao em lote (JSON/XML): escolher pasta e log."""

    def _escolherPasta(self):
        pasta = QtWidgets.QFileDialog.getExistingDirectory(self, 'Selecione a pasta de saída')
        if pasta:
            self.pastaLe.setText(pasta)

    def _appendLog(self, txt):
        self.log.appendPlainText(txt)
