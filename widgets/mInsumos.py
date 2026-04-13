# -*- coding: utf-8 -*-
import os, json, re
from qgis.PyQt import QtCore, QtWidgets
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsProject
from SAP_Gerente.widgets.mDialog import MDialog
from .addInsumoForm import AddInsumoForm

class MInsumos(MDialog):

    def __init__(self, controller, qgis, sap):
        super(MInsumos, self).__init__(controller=controller)
        self.sap = sap
        self._availableGroupIds = set()
        self.addInsumoFormDlg = None
        self.tableWidget.setColumnHidden(7, True)
        self.loadGrupos(self.sap.getInputGroups())
        self.loadTipos(self.sap.getInputTypes())
        self.fetchData()
        self.setWindowTitle('Gerenciador de Insumos')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mInsumos.ui'
        )

    def getColumnsIndexToSearch(self):
        return [0, 2, 3, 5, 6]

    def loadGrupos(self, data):
        self._availableGroupIds = {item['id'] for item in data}
        self.grupoInsumoCb.clear()
        self.grupoInsumoCb.addItem('Todos', '')
        for item in data:
            self.grupoInsumoCb.addItem(item['nome'], item['id'])

    def loadTipos(self, data):
        self.tipoInsumoCb.clear()
        self.tipoInsumoCb.addItem('Todos', '')
        for item in data:
            self.tipoInsumoCb.addItem(item['nome'], item['code'])

    def fetchData(self):
        grupoId = self.grupoInsumoCb.itemData(self.grupoInsumoCb.currentIndex())
        tipoCode = self.tipoInsumoCb.itemData(self.tipoInsumoCb.currentIndex())
        data = self.sap.getInsumos(
            grupoId if grupoId else None,
            tipoCode if tipoCode else None
        )
        data = [r for r in data if r.get('grupo_insumo_id') in self._availableGroupIds]
        self.addRows(data)

    def addRows(self, data):
        self.clearAllItems()
        for row in data:
            self.addRow(
                row['id'],
                row['nome'],
                row['caminho'],
                row.get('epsg', ''),
                row.get('tipo_insumo', ''),
                row.get('grupo_insumo', ''),
                row
            )
        self.adjustColumns()

    def addRow(self, rowId, nome, caminho, epsg, tipoInsumo, grupoInsumo, rowData):
        idx = self.getRowIndex(rowId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(rowId))
        self.tableWidget.setCellWidget(idx, 1, self.createOptionWidget(idx))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(nome))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(caminho))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(str(epsg) if epsg else ''))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(tipoInsumo))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(grupoInsumo))
        self.tableWidget.setItem(idx, 7, self.createNotEditableItem(json.dumps(rowData, ensure_ascii=False)))

    def createOptionWidget(self, row):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        for button in self.getRowOptionSetup(row):
            btn = self.createTableToolButton(button['tooltip'], button['iconPath'])
            btn.clicked.connect(button['callback'])
            layout.addWidget(btn)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return wd

    def getRowOptionSetup(self, row):
        return [
            {
                'tooltip': 'Editar',
                'iconPath': self.getEditIconPath(),
                'callback': lambda b, row=row: self.handleEdit(row)
            },
            {
                'tooltip': 'Excluir',
                'iconPath': self.getTrashIconPath(),
                'callback': lambda b, row=row: self.handleDelete(row)
            },
            {
                'tooltip': 'Carregar geometria no QGIS',
                'iconPath': self.getUploadIconPath(),
                'callback': lambda b, row=row: self.handleLoad(row)
            }
        ]

    def getRowIndex(self, rowId):
        if not rowId:
            return -1
        for idx in range(self.tableWidget.rowCount()):
            if rowId == self.tableWidget.model().index(idx, 0).data():
                return idx
        return -1

    def getRowData(self, rowIndex):
        raw = self.tableWidget.model().index(rowIndex, 7).data()
        return json.loads(raw)

    def handleEdit(self, row):
        currentData = self.getRowData(row)
        if self.addInsumoFormDlg:
            self.addInsumoFormDlg.close()
        self.addInsumoFormDlg = AddInsumoForm(self.sap, self)
        self.addInsumoFormDlg.setData(
            currentData['id'],
            currentData['nome'],
            currentData['caminho'],
            currentData.get('epsg', ''),
            currentData.get('geom'),
            currentData.get('grupo_insumo_id'),
            currentData.get('tipo_insumo_id')
        )
        self.addInsumoFormDlg.accepted.connect(self.fetchData)
        self.addInsumoFormDlg.show()

    def handleDelete(self, row):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir o insumo?\nNão é possível excluir insumos associados a unidades de trabalho.')
        if not result:
            return
        try:
            message = self.sap.deleteInsumos([int(self.getRowData(row)['id'])])
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))
        finally:
            self.fetchData()

    def handleLoad(self, row):
        rowData = self.getRowData(row)
        ewkt = rowData.get('geom')
        if not ewkt:
            self.showError('Aviso', 'Este insumo não possui geometria cadastrada.')
            return
        wkt = re.sub(r'^SRID=\d+;', '', ewkt)
        layer = QgsVectorLayer('Polygon?crs=EPSG:4326', rowData.get('nome', 'insumo'), 'memory')
        provider = layer.dataProvider()
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(wkt))
        provider.addFeature(feature)
        QgsProject.instance().addMapLayer(layer)

    @QtCore.pyqtSlot(bool)
    def on_filterBtn_clicked(self):
        self.fetchData()
