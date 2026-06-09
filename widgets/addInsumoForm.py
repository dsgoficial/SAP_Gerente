import os
from qgis.PyQt import QtCore, QtWidgets
from SAP_Gerente.widgets.inputDialogV2 import InputDialogV2

class AddInsumoForm(InputDialogV2):

    def __init__(self, sap, parent=None):
        super(AddInsumoForm, self).__init__(parent=parent)
        self.sap = sap
        self.currentId = None
        self.currentGeom = None
        self.loadGrupos(self.sap.getAllInputGroups())
        self.loadTipos(self.sap.getInputTypes())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addInsumoForm.ui'
        )

    def loadGrupos(self, data):
        self.grupoInsumoCb.clear()
        for item in data:
            self.grupoInsumoCb.addItem(item['nome'], item['id'])

    def loadTipos(self, data):
        self.tipoInsumoCb.clear()
        for item in data:
            self.tipoInsumoCb.addItem(item['nome'], item['code'])

    def validInput(self):
        return bool(self.nomeLe.text() and self.caminhoLe.text())

    def getData(self):
        data = {
            'nome': self.nomeLe.text(),
            'caminho': self.caminhoLe.text(),
            'epsg': self.epsgLe.text(),
            'geom': self.currentGeom,
            'grupo_insumo_id': self.grupoInsumoCb.itemData(self.grupoInsumoCb.currentIndex()),
            'tipo_insumo_id': self.tipoInsumoCb.itemData(self.tipoInsumoCb.currentIndex()),
        }
        if self.currentId:
            data['id'] = self.currentId
        return data

    def setData(self, currentId, nome, caminho, epsg, geom, grupoInsumoId, tipoInsumoId):
        self.currentId = currentId
        self.currentGeom = geom
        self.nomeLe.setText(nome or '')
        self.caminhoLe.setText(caminho or '')
        self.epsgLe.setText(str(epsg) if epsg else '')
        self.grupoInsumoCb.setCurrentIndex(self.grupoInsumoCb.findData(grupoInsumoId))
        self.tipoInsumoCb.setCurrentIndex(self.tipoInsumoCb.findData(tipoInsumoId))

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showError('Aviso', 'Preencha os campos Nome e Caminho!')
            return
        try:
            message = self.sap.updateInsumos([self.getData()])
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.close()
