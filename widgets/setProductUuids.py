import os, re
from qgis.PyQt import QtCore, QtWidgets, uic


VALID_UUID_RE = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
)

COL_MI   = 0
COL_INOM = 1
COL_NOME = 2
COL_UUID_ATUAL = 3
COL_UUID_NOVO  = 4
COL_ID   = 5


class SetProductUuids(QtWidgets.QDialog):

    def __init__(self, controller, qgis, sap, parent=None):
        super(SetProductUuids, self).__init__(parent=parent)
        uic.loadUi(self._getUiPath(), self)
        self.sap = sap
        self._products = {}
        self.setWindowTitle('Definir UUID dos Produtos')
        self.tableWidget.setColumnHidden(COL_ID, True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.loadBtn.clicked.connect(self._loadProducts)
        self.applyBtn.clicked.connect(self._apply)
        self.searchLe.textChanged.connect(self._filterRows)
        self._populateLotCombo()

    def _getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'setProductUuids.ui'
        )

    def _populateLotCombo(self):
        self.lotCb.clear()
        self.lotCb.addItem('...', None)
        try:
            for lot in (self.sap.getAllLots() or []):
                if lot:
                    self.lotCb.addItem(lot.get('nome', ''), lot.get('id'))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro ao carregar lotes', str(e))

    def _loadProducts(self):
        lote_id = self.lotCb.itemData(self.lotCb.currentIndex())
        if not lote_id:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um lote.')
            return
        try:
            produtos = self.sap.getProductsByLot(lote_id) or []
            self._products = {p['id']: p for p in produtos}
            self._fillTable(produtos)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))

    def _fillTable(self, produtos):
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setRowCount(0)
        for p in produtos:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, COL_MI,   self._roItem(p.get('mi', '') or ''))
            self.tableWidget.setItem(row, COL_INOM,  self._roItem(p.get('inom', '') or ''))
            self.tableWidget.setItem(row, COL_NOME,  self._roItem(p.get('nome', '') or ''))
            self.tableWidget.setItem(row, COL_UUID_ATUAL, self._roItem(p.get('uuid', '') or ''))
            self.tableWidget.setItem(row, COL_UUID_NOVO,  QtWidgets.QTableWidgetItem(''))
            self.tableWidget.setItem(row, COL_ID,    self._roItem(str(p['id'])))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setSortingEnabled(True)

    def _filterRows(self, text):
        text = text.strip().lower()
        for row in range(self.tableWidget.rowCount()):
            visible = not text or any(
                text in (self.tableWidget.item(row, col).text() or '').lower()
                for col in (COL_MI, COL_INOM, COL_NOME, COL_UUID_ATUAL)
            )
            self.tableWidget.setRowHidden(row, not visible)

    def _roItem(self, text):
        item = QtWidgets.QTableWidgetItem(str(text))
        item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)
        return item

    def _apply(self):
        to_update = []
        invalid = []
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.isRowHidden(row):
                continue
            new_uuid = self.tableWidget.item(row, COL_UUID_NOVO).text().strip()
            if not new_uuid:
                continue
            if not VALID_UUID_RE.match(new_uuid):
                mi = self.tableWidget.item(row, COL_MI).text()
                inom = self.tableWidget.item(row, COL_INOM).text()
                invalid.append(mi or inom)
                continue
            produto_id = int(self.tableWidget.item(row, COL_ID).text())
            p = self._products[produto_id]
            to_update.append({
                'id': produto_id,
                'uuid': new_uuid,
                'nome': p.get('nome', ''),
                'mi': p.get('mi') or '',
                'inom': p.get('inom') or '',
                'edicao': p.get('edicao') or '',
                'denominador_escala': str(p.get('denominador_escala', '')),
            })
        if invalid:
            QtWidgets.QMessageBox.warning(
                self, 'UUID invalido',
                'UUID invalido nos produtos: {}'.format(', '.join(invalid))
            )
            return
        if not to_update:
            QtWidgets.QMessageBox.information(self, 'Aviso', 'Nenhum UUID novo preenchido.')
            return
        try:
            message = self.sap.updateProducts(to_update)
            QtWidgets.QMessageBox.information(
                self, 'Aviso',
                message or '{} produto(s) atualizado(s).'.format(len(to_update))
            )
            self._loadProducts()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', str(e))
