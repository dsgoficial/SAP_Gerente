import os, sys, copy
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory
from qgis import core, gui
from qgis.utils import iface
import json
from SAP_Gerente.factories.functionsSettingsSingleton import FunctionsSettingsSingleton
from SAP_Gerente.modules.sap.api.contrato import (
    pacoteEhBaseVersionada, versionamentoDoPacote, ErroVersionamento, mensagemErroCampo
)

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
        # SAP 3.0: `PUT /iniciar_modo_local` recebe só `atividade_id`; quem
        # executou é informado ao finalizar (public.sap_local.usuario_uuid).
        self.userCb.setVisible(False)
        self.label_3.setVisible(False)
        self.criarCampoPasta()

    def criarCampoPasta(self):
        # Base versionada (tipo 4, contrato 9.4): o clone da atividade vai a
        # campo num GeoPackage gravado nesta pasta, ao lado do pacote local, e
        # o pacote guarda só o nome do arquivo e o SHA-256.
        self.pastaLabel = QtWidgets.QLabel('Pasta do arquivo de campo (base versionada):', self)
        self.pastaCampoFw = gui.QgsFileWidget(self)
        self.pastaCampoFw.setStorageMode(gui.QgsFileWidget.StorageMode.GetDirectory)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.pastaLabel)
        layout.addWidget(self.pastaCampoFw, 1)
        # A linha entra acima dos botões, que descem uma posição.
        self.gridLayout.removeItem(self.horizontalLayout_2)
        self.gridLayout.addLayout(layout, 4, 0)
        self.gridLayout.addLayout(self.horizontalLayout_2, 5, 0)

    def getFieldFolder(self):
        return (self.pastaCampoFw.filePath() or '').strip()

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
                    key=lambda user: user['rotulo']
                ):
            self.userCb.addItem(
                user['rotulo'],
                user['uuid']
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
            values = self.controller.getValuesFromLayer('sapLocalActivity', 'activity', raiseOnError=True)
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
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        iniciado = False
        try:
            activityId = int(self.activityIdLe.text())
            dbData = json.loads(self.dbCb.itemData(self.dbCb.currentIndex()))
            activityData = self.sap.getActivityDataById(activityId)
            versionada = pacoteEhBaseVersionada(activityData)
            pasta = self.getFieldFolder()
            if versionada and not (pasta and os.path.isdir(pasta)):
                QtWidgets.QApplication.restoreOverrideCursor()
                self.showError(
                    'Aviso',
                    'O dado de produção desta atividade é uma Base versionada: escolha a pasta '
                    'onde gravar o arquivo de campo.'
                )
                return
            # O banco local é conferido ANTES de iniciar o modo local, que muda a
            # atividade no servidor.
            self.sap.checkSAPLocalDatabase(dbData)
            if self.sap.startLocalMode(activityId) is None:
                # A recusa já foi mostrada por `checkError`.
                QtWidgets.QApplication.restoreOverrideCursor()
                return
            iniciado = True
            if versionada:
                # O clone da atividade nasce no `iniciar_modo_local`: o pacote
                # lido antes dele não tem o `repo_id`, e é lido de novo.
                activityData = self.sap.getActivityDataById(activityId)
                versionamento = versionamentoDoPacote(activityData)
                if versionamento is None:
                    raise Exception('O pacote da atividade não trouxe a seção "versionamento".')
                nome, sha256 = self.sap.downloadFieldFile(activityId, pasta, versionamento.get('repo_id'))
                versionamento['arquivo'] = nome
                versionamento['sha256'] = sha256
            # O FME saiu do SAP 3.0 (2026-10-14), mas o servidor ainda manda a chave
            # `fme` ao Operador velho ate a fase 4; ela nao entra no pacote local.
            activityData['dados']['atividade'].pop('fme', None)
            activityData['dados']['atividade'].pop('insumos', None)
            activityData['dados'].pop('login_info', None)
            activityData['local_db'] = dbData
            self.sap.exportToSAPLocal(activityData)
            QtWidgets.QApplication.restoreOverrideCursor()
            if versionada:
                self.showInfo('Aviso', 'Executado com sucesso! Arquivo de campo: {0}'.format(nome))
            else:
                self.showInfo('Aviso', 'Executado com sucesso!')
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            mensagem = mensagemErroCampo(e) if isinstance(e, ErroVersionamento) else str(e)
            if iniciado:
                mensagem = (
                    '{0}\n\nO modo local já foi iniciado no servidor. Para configurar de novo, '
                    'reinicie a atividade (o que descarta o clone de campo, na base versionada).'
                ).format(mensagem)
            self.showError('Aviso', mensagem)

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