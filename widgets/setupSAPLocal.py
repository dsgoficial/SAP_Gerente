import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory
from qgis import core, gui
from qgis.utils import iface
import json
from SAP_Gerente.factories.functionsSettingsSingleton import FunctionsSettingsSingleton

class SetupSAPLocal(QtWidgets.QDialog):

    def __init__(self, 
            users,
            controller, 
            qgis, 
            sap,
            functionsSettings=FunctionsSettingsSingleton.getInstance(),
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(SetupSAPLocal, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.controller = controller
        self.users = users
        self.qgis = qgis
        self.sap = sap
        self.functionsSettings = functionsSettings
        self.messageFactory = messageFactory
        self.loadIconBtn(self.extractFieldBtn, self.getExtractIconPath(), 'Extrair valores mediante seleções')
        self.setWindowTitle('Configurar SAP Local')
        self.loadDatabases()
        self.loadUsers(self.users)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "setupSAPLocal.ui"
        )

    def loadIconBtn(self, button, pathIcon, toolTip):
        button.setIcon(QtGui.QIcon(pathIcon))
        button.setIconSize(QtCore.QSize(24,24))
        button.setToolTip(toolTip)

    def getExtractIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'extract.png'
        )

    def loadDatabases(self):
        dbs = self.getDatabaseSettings()
        self.dbCb.clear()
        self.dbCb.addItem('...', None)
        for db in dbs:
            self.dbCb.addItem(db['alias'], json.dumps(db))

    def loadUsers(self, users):
        for user in sorted(
                    users, 
                    key=lambda user: '{0} {1}'.format(user['tipo_posto_grad'], user['nome_guerra'])
                ):
            self.userCb.addItem(
                '{0} {1}'.format(user['tipo_posto_grad'], user['nome_guerra']), 
                user['id']
            )

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
        )

    def showError(self, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showInfo(self, title, message):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)

    @QtCore.pyqtSlot(bool)
    def on_extractFieldBtn_clicked(self):
        try:
            values = self.controller.getValuesFromLayerV2('sapLocalActivity', 'activity')
            if len(values.split(',')) != 1:
                self.showError('Aviso', "Selecione apenas uma unidade de trabalho!")
                return
            self.activityIdLe.setText(values)
        except Exception as e:
            self.showError('Aviso', str(e))
        
    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        activityId = int(self.activityIdLe.text())
        userId = self.userCb.itemData(self.userCb.currentIndex())
        activityData = self.sap.getActivityDataById(activityId)
        del activityData['dados']['atividade']['fme']
        del activityData['dados']['atividade']['insumos']
        del activityData['dados']['login_info']
        activityData['local_db'] = json.loads(self.dbCb.itemData(self.dbCb.currentIndex()))
        try:
            self.sap.startLocalMode(activityId, userId)
            self.sap.exportToSAPLocal(activityData)
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showInfo('Aviso', 'Executado com sucesso!')
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Aviso', str(e))        

    def validInput(self):
        try:
            int(self.activityIdLe.text())
        except Exception as e:
            self.showError('Aviso', 'Campo "ID da atividade" deve ser preenchido com um número!')
            return False 
        if not (
                self.dbCb.itemData(self.dbCb.currentIndex())
                and
                self.activityIdLe.text()
            ):
            self.showError('Aviso', "<p>Preencha todas as entradas ou entrada inválida!</p>")
            return False
        return True