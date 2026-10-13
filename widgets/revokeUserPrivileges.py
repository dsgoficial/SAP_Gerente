import os, sys, copy
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
from SAP_Gerente.modules.sap.api.contrato import (
    emAndamento, TIPOS_COM_BANCO, ehTipo, rotuloDadoProducao
)
 
class  RevokeUserPrivileges(DockWidget):

    def __init__(self, databases, controller, sap):
        super(RevokeUserPrivileges, self).__init__(controller=controller)
        self.setWindowTitle('Revogar Permissões Usuário')
        self.sap = sap
        self.databases = databases
        self.loadCombo(
            self.usersCb, 
            [
                {'id': d['uuid'], 'value': d['rotulo']}
                for d in self.sap.getActiveUsers()
            ]    
        )
        self.loadCombo(
            self.databasesCb, 
            [
                {'id': d['id'], 'value': rotuloDadoProducao(d)}
                for d in self.databases
                # Só banco PostgreSQL (tipos 2 e 3), nunca a base versionada.
                if emAndamento(d, 'lote_status_execucao_id') and ehTipo(d, TIPOS_COM_BANCO)
            ]
        )

    def loadCombo(self, combo, data):
        combo.clear()
        combo.addItem('...', None)
        for row in data:
            combo.addItem(row['value'], row['id'])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "revokeUserPrivileges.ui"
        )

    def getDatabaseData(self, dbName):
        for dbData in self.databases:
            if not ( dbData['nome'] == dbName ):
                continue
            return dbData

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        data = self.getData()
        if not(
                data and
                data['dado_producao_id'] and
                data['usuario_uuid']
            ):
            self.showError('Aviso', 'Preencha os dados!')
            return
        message = self.sap.revokeUserPrivileges(data)
        message and self.showInfo('Aviso', message)

    def getData(self):
        # SAP 3.0: o banco é o `dado_producao_id` e a pessoa é o `usuario_uuid`.
        return  {
            "dado_producao_id" : self.databasesCb.itemData(self.databasesCb.currentIndex()),
            "usuario_uuid" : self.usersCb.itemData(self.usersCb.currentIndex())
        }