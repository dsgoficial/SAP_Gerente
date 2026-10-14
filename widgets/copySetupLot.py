import os, sys
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class CopySetupLot(InputDialogV2):

    def __init__(
            self, 
            sap,
            parent=None
        ):
        super(CopySetupLot, self).__init__(parent=parent)
        self.setWindowTitle('Copiar Configurações do Lote')
        self.sap = sap
        
        self.loadCombo(
            self.lotDestCb,
            [
                {'id': i['id'], 'value': i['nome']} 
                for i in self.sap.getLots()
            ]
        )
        
        self.lotDestCb.currentIndexChanged.connect(self.updateSourceLots)
        
        # Inicia o combo de origem vazio
        self.loadCombo(self.lotSourceCb, [])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'copySetupLot.ui'
        )

    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    def updateSourceLots(self, index):
        # Limpa o combo de origem
        self.lotSourceCb.clear()
        self.lotSourceCb.addItem('...', None)
        
        # Obtém o ID do lote destino selecionado
        dest_lot_id = self.lotDestCb.itemData(index)
        
        if dest_lot_id:
            # SAP 3.0: o lote é do acervo e não tem linha de produção; as linhas
            # que um lote executa saem das ETAPAS dele. A origem é todo lote que
            # executa alguma linha do destino (o servidor recusa a cópia de
            # subfase de linha que o destino não executa). Destino ainda sem
            # etapa: todos os lotes, e o servidor explica a recusa.
            linhas = {}
            for etapa in self.sap.getSteps():
                linhas.setdefault(etapa['lote_id'], set()).add(etapa['linha_producao_id'])
            linhasDestino = linhas.get(dest_lot_id, set())
            source_lots = [
                {'id': lot['id'], 'value': lot['nome']}
                for lot in self.sap.getLots()
                if lot['id'] != dest_lot_id
                and (not linhasDestino or linhas.get(lot['id'], set()) & linhasDestino)
            ]

            for lot in source_lots:
                self.lotSourceCb.addItem(lot['value'], lot['id'])

    def getData(self):
        data = {
            "lote_id_origem": self.lotSourceCb.itemData(self.lotSourceCb.currentIndex()),
            "lote_id_destino": self.lotDestCb.itemData(self.lotDestCb.currentIndex()),
            "copiar_estilo": self.styleCkb.isChecked(),
            "copiar_menu": self.menuCkb.isChecked(),
            "copiar_regra": self.ruleCkb.isChecked(),
            "copiar_modelo": self.modelCkb.isChecked(),
            "copiar_workflow": self.worflowCkb.isChecked(),
            "copiar_alias": self.aliasCkb.isChecked(),
            "copiar_linhagem": self.lineageProfileCkb.isChecked(),
            "copiar_finalizacao": self.completionRequirementCkb.isChecked(),
            "copiar_tema": self.themeCkb.isChecked(),
            "copiar_colunas_ocultas": self.hiddenColumnsCkb.isChecked(),
            # O FME saiu do SAP 3.0 (2026-10-14). O servidor 3.36.0 ainda exige a
            # chave na copia entre lotes; ela sai na fase 4, quando o servidor
            # deixar de exigi-la.
            "copiar_fme": False,
            "copiar_configuracao_qgis": self.qgisCb.isChecked(),
            "copiar_monitoramento": self.monitoringCb.isChecked(),
        }
        return data

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            data = self.getData()
            if not (
                data['lote_id_origem'] and
                data['lote_id_destino']
            ):
                self.showError('Aviso', 'Defina o lote de origem e destino!')
                return
            QtWidgets.QApplication.restoreOverrideCursor()
            message = self.sap.copySetupLot(self.getData())
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Aviso', str(e))