import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory
from qgis import core, gui
from qgis.utils import iface
import json

class EndSAPLocal(QtWidgets.QDialog):

    def __init__(self, 
            controller, 
            qgis, 
            sap,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(EndSAPLocal, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.messageFactory = messageFactory
        self.setWindowTitle('Finalizar SAP Local')
        self.loadDatabases()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "endSAPLocal.ui"
        )

    def loadDatabases(self):
        dbs = self.getDatabaseSettings()
        self.dbCb.clear()
        self.dbCb.addItem('...', None)
        for db in dbs:
            self.dbCb.addItem(db['alias'], db)

    def getDatabaseSettings(self):
        dbaliases = sorted([ 
            key.split('/')[2] 
            for key in QtCore.QSettings().allKeys() 
            if 'postgresql' in key.lower() 
                and 
                'host' in key.lower() 
                and 
                len(key.split('/')) > 3
        ])
        dbsettings = []
        for dbalias in dbaliases:
            if not self.isValidDatabaseSettings(dbalias):
                continue
            dbsettings.append({
                'alias': dbalias,
                'database': QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/database'),
                'host': QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/host'),
                'port': QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/port'),
                'username': QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/username'),
                'password': QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/password'),
            })
        return dbsettings

    def isValidDatabaseSettings(self, dbalias):
        return (
            QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/savePassword') == 'true'
            and
            QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/saveUsername') == 'true'
            and
            self.sap.validDBEndLocalMode(
                QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/database'),
                QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/host'),
                QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/port'),
                QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/username'),
                QtCore.QSettings().value('PostgreSQL/connections/'+dbalias+'/password')
            )
        )

    def showError(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showInfo(self, title, message):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        dbData = self.dbCb.itemData(self.dbCb.currentIndex())
        try:
            self.sap.endLocalMode(dbData)
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showInfo('Aviso', 'Executado com sucesso!')
        except Exception as e:
           QtWidgets.QApplication.restoreOverrideCursor()
           self.showError('Aviso', str(e))        

    def validInput(self):
        if not (
                self.dbCb.itemData(self.dbCb.currentIndex())
            ):
            self.showError('Aviso', "<p>Selecione o banco de dados!</p>")
            return False
        return True