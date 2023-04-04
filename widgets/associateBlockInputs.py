import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2
 
class AssociateBlockInputs(InputDialogV2):

    def __init__(self, inputGroups, controller, qgis, sap):
        super(AssociateBlockInputs, self).__init__(controller=controller)
        self.sap = sap
        self.loadCombo(
            self.inputGroupsCb, 
            [ {'id': d['id'], 'value': d['nome']} for d in inputGroups]
        )
        self.loadCombo(
            self.associationStrategyCb, 
            [ {'id': d['code'], 'value': d['nome']} for d in self.controller.getSapAssociationStrategies()]
        )
        self.loadCombo(
            self.blocksCb, 
            [ {'id': d['id'], 'value': d['nome']} for d in self.sap.getBlocks()]
        )
        self.setWindowTitle('Associar Insumos')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "associateBlockInputs.ui"
        )

    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    def validInput(self):
        return (
            self.workspacesIdLe.text()
        )

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        data = self.getData()
        if not ( 
            data['bloco_id'] and data['grupo_insumo_id'] and data['estrategia_id']
        ):
            self.showError('Aviso', 'Preencha os dados!')
            return
        message = self.sap.createBlockInputs(data)
        self.showInfo('Aviso', message)
      
    def getData(self):
        return {
            'bloco_id': self.blocksCb.itemData(self.blocksCb.currentIndex()),
            'grupo_insumo_id': self.inputGroupsCb.itemData(self.inputGroupsCb.currentIndex()),
            'estrategia_id': self.associationStrategyCb.itemData(self.associationStrategyCb.currentIndex()),
            'caminho_padrao': self.defaultPathLe.text()
        }  