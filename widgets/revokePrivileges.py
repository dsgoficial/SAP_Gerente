import os, sys, copy
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
from SAP_Gerente.modules.sap.api.contrato import (
    emAndamento, TIPOS_COM_BANCO, ehTipo, rotuloDadoProducao
)
 
class  RevokePrivileges(DockWidget):

    def __init__(self, databases, sapCtrl):
        super(RevokePrivileges, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Revogar Permissões')
        self.databases = databases
        self.loadDatabases(self.databases)
        
    def loadDatabases(self, databases):
        self.databases = databases
        self.databasesCb.clear()
        self.databasesCb.addItem('...', None)
        # Só banco PostgreSQL (tipos 2 e 3): a base versionada não tem permissão
        # de banco a revogar.
        for d in self.databases:
            if emAndamento(d, 'lote_status_execucao_id') and ehTipo(d, TIPOS_COM_BANCO):
                self.databasesCb.addItem(rotuloDadoProducao(d), d['id'])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "revokePrivileges.ui"
        )

    def getDatabases(self):
        return self.databases

    def getDatabaseData(self, dbName):
        for dbData in self.getDatabases():
            if not ( dbData['nome'] == dbName ):
                continue
            return dbData

    def getCurrentDatabase(self):
        return self.databasesCb.currentText()

    def clearInput(self):
        pass

    def validDatabase(self):
        return self.databasesCb.currentIndex() != 0

    def validInput(self):
        return  self.validDatabase()

    def runFunction(self):
        dadoProducaoId = self.databasesCb.itemData(self.databasesCb.currentIndex())
        if dadoProducaoId is None:
            return
        self.controller.revokeSapPrivileges(dadoProducaoId)