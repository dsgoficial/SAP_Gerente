import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class  RevokeUserPrivileges(DockWidget):

    def __init__(self, databases, controller, sap):
        super(RevokeUserPrivileges, self).__init__(controller=controller)
        self.setWindowTitle('Revogar Permissões Usuário')
        self.sap = sap
        self.databases = databases
        self.loadCombo(
            self.usersCb, 
            [
                {'id': d['id'], 'value': '{} {}'.format(d['tipo_posto_grad'], d['nome_guerra'])} 
                for d in self.sap.getUsers()
            ]    
        )
        self.loadCombo(
            self.databasesCb, 
            [{'id': d['id'], 'value': d['nome']} for d in self.databases]    
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
                data['servidor'] and
                data['porta'] and
                data['banco'] and
                data['usuario_id']
            ):
            self.showError('Aviso', 'Preencha os dados!')
            return
        message = self.sap.revokeUserPrivileges(data)
        self.showInfo('Aviso', message)

    def getData(self):
        dbData = self.getDatabaseData(self.databasesCb.currentText())
        if dbData is None and self.usersCb.itemData(self.usersCb.currentIndex()) :
            return
        return  {
            "servidor" : dbData['servidor'],
            "porta" : int(dbData['porta']),
            "banco" : dbData['nome'],
            "usuario_id" : int(self.usersCb.itemData(self.usersCb.currentIndex()))
        }