import os, json, re
from qgis.PyQt import QtCore, QtWidgets

_UUID_RE = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
from SAP_Gerente.widgets.mDialogV3 import MDialogV3


class MProducts(MDialogV3):

    def __init__(self, controller, qgis, sap, parent=None):
        super(MProducts, self).__init__(controller, parent=parent)
        self.sap = sap
        self.qgis = qgis
        self._products = []
        self.setWindowTitle('Produtos')
        self.showAllLotsCheckBox.setChecked(False)
        self.showAllLotsCheckBox.stateChanged.connect(self._populateLotCombo)
        self._populateLotCombo()
        self.tableWidget.setColumnHidden(8, True)
        self.adjustColumns()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mProducts.ui'
        )

    def _populateLotCombo(self):
        self.lotCb.clear()
        self.lotCb.addItem('...', None)
        lots = self.sap.getAllLots() or []
        if not self.showAllLotsCheckBox.isChecked():
            lots = [lot for lot in lots if lot.get('status_id') == 1]
        lots = sorted(lots, key=lambda l: l.get('nome', ''))
        for lot in lots:
            if lot:
                self.lotCb.addItem(lot.get('nome', ''), lot.get('id'))

    @QtCore.pyqtSlot(bool)
    def on_loadBtn_clicked(self):
        lote_id = self.lotCb.itemData(self.lotCb.currentIndex())
        if not lote_id:
            self.showError('Aviso', 'Selecione um lote.')
            return
        try:
            self._products = self.sap.getProductsByLot(lote_id) or []
            self.addRows(self._products)
        except Exception as e:
            self.showError('Erro', str(e))

    def addRows(self, data):
        self.clearAllItems()
        for row in data:
            self.addRow(row)

    def addRow(self, p):
        idx = self.tableWidget.rowCount()
        self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(p.get('id')))
        self.tableWidget.setCellWidget(idx, 1, self._createDeleteWidget(idx))
        self.tableWidget.setItem(idx, 2, self.createEditableItem(p.get('nome', '')))
        self.tableWidget.setItem(idx, 3, self.createEditableItem(p.get('mi', '')))
        self.tableWidget.setItem(idx, 4, self.createEditableItem(p.get('inom', '')))
        self.tableWidget.setItem(idx, 5, self.createEditableItem(str(p.get('edicao', '') or '')))
        self.tableWidget.setItem(idx, 6, self.createEditableItem(str(p.get('denominador_escala', '') or '')))
        self.tableWidget.setItem(idx, 7, self.createEditableItem(p.get('uuid', '')))
        self.tableWidget.setItem(idx, 8, self.createNotEditableItem(json.dumps(p)))

    def _createDeleteWidget(self, row):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, 1))
        deleteBtn = self.createToolButton(self.tableWidget, 'Deletar', self.getDeleteIconPath())
        deleteBtn.clicked.connect(lambda *args, idx=index: self._handleDelete(idx))
        layout.addWidget(deleteBtn)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return wd

    def _handleDelete(self, index):
        row = index.row()
        produto_id = self.tableWidget.model().index(row, 0).data()
        if not self.showQuestion('Deletar', 'Deletar produto {}?'.format(produto_id)):
            return
        try:
            message = self.sap.deleteProducts([int(produto_id)])
            self.tableWidget.removeRow(row)
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Erro', str(e))

    @QtCore.pyqtSlot(bool)
    def on_saveBtn_clicked(self):
        produtos = []
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.isRowHidden(row):
                continue
            dump = self.tableWidget.model().index(row, 8).data()
            original = json.loads(dump) if dump else {}
            produto_id = self.tableWidget.model().index(row, 0).data()
            try:
                denom = self.tableWidget.model().index(row, 6).data()
                uuid = self.tableWidget.model().index(row, 7).data() or original.get('uuid', '') or ''
                if uuid and not _UUID_RE.match(uuid):
                    nome = self.tableWidget.model().index(row, 2).data() or str(produto_id)
                    self.showError('UUID inválido', 'UUID inválido no produto: {}'.format(nome))
                    return
                produtos.append({
                    'id': int(produto_id),
                    'uuid': uuid,
                    'nome': self.tableWidget.model().index(row, 2).data() or '',
                    'mi': self.tableWidget.model().index(row, 3).data() or '',
                    'inom': self.tableWidget.model().index(row, 4).data() or '',
                    'edicao': self.tableWidget.model().index(row, 5).data() or '',
                    'denominador_escala': str(denom).strip() if denom and str(denom).strip() else str(original.get('denominador_escala', '')),
                })
            except Exception as e:
                self.showError('Erro na linha {}'.format(row + 1), str(e))
                return
        if not produtos:
            self.showError('Aviso', 'Nenhum produto para salvar.')
            return
        try:
            message = self.sap.updateProducts(produtos)
            self.showInfo('Aviso', message or 'Produtos atualizados com sucesso.')
            self.on_loadBtn_clicked()
        except Exception as e:
            self.showError('Erro', str(e))

    @QtCore.pyqtSlot(bool)
    def on_loadQgisBtn_clicked(self):
        if not self._products:
            self.showError('Aviso', 'Carregue os produtos primeiro.')
            return
        try:
            self._loadAsQgisLayer(self._products)
            self.showInfo('QGIS', 'Camada "Produtos SAP" adicionada ao projeto.')
        except Exception as e:
            self.showError('Erro', str(e))

    def _loadAsQgisLayer(self, products):
        from qgis.core import (
            QgsVectorLayer, QgsFeature, QgsGeometry,
            QgsField, QgsProject
        )
        from qgis.PyQt.QtCore import QVariant

        layer = QgsVectorLayer('MultiPolygon?crs=epsg:4326', 'Produtos SAP', 'memory')
        pr = layer.dataProvider()
        pr.addAttributes([
            QgsField('id', QVariant.Int),
            QgsField('nome', QVariant.String),
            QgsField('mi', QVariant.String),
            QgsField('inom', QVariant.String),
            QgsField('edicao', QVariant.String),
            QgsField('denom_escala', QVariant.Int),
            QgsField('uuid', QVariant.String),
        ])
        layer.updateFields()
        features = []
        for p in products:
            raw_geom = p.get('geom') or p.get('geometria')
            if not raw_geom:
                continue
            geom_wkt = raw_geom.split(';', 1)[-1] if ';' in raw_geom else raw_geom
            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromWkt(geom_wkt))
            denom = p.get('denominador_escala')
            f.setAttributes([
                p.get('id'),
                p.get('nome', ''),
                p.get('mi', ''),
                p.get('inom', ''),
                str(p.get('edicao', '') or ''),
                int(denom) if denom else None,
                p.get('uuid', ''),
            ])
            features.append(f)
        pr.addFeatures(features)
        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)

    def getRowData(self, row):
        dump = self.tableWidget.model().index(row, 8).data()
        return json.loads(dump) if dump else {}
