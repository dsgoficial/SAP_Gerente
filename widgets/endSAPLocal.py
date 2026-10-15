import os, sys, copy
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory
from qgis import core, gui
from qgis.utils import iface
import json
from SAP_Gerente.modules.sap.api.contrato import ErroVersionamento, mensagemErroCampo, versionamentoDoPacote

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
        self.criarCampoPasta()

    def criarCampoPasta(self):
        # Base versionada (tipo 4, contrato 9.4): a pasta onde está o arquivo de
        # campo que o "Configurar SAP Local" baixou (o nome está no pacote).
        self.pastaLabel = QtWidgets.QLabel('Pasta do arquivo de campo:', self)
        self.pastaCampoFw = gui.QgsFileWidget(self)
        self.pastaCampoFw.setStorageMode(gui.QgsFileWidget.StorageMode.GetDirectory)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.pastaLabel)
        layout.addWidget(self.pastaCampoFw, 1)
        # A linha entra acima dos botões, que descem uma posição.
        self.gridLayout.removeItem(self.horizontalLayout_2)
        self.gridLayout.addLayout(layout, 1, 0)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0)

    def getFieldFolder(self):
        return (self.pastaCampoFw.filePath() or '').strip() or None

    def resolverConflito(self, erro, pacote):
        # O 409 `conflito_versionamento` do `finalizar_modo_local`: abre a
        # resolução do módulo comum (`modules/versionamento`, cópia do SAP
        # Operador) sobre a sessão que o servidor informou. Devolve True para
        # finalizar de novo; sem o módulo, ou com a tela fechada, False, e quem
        # chamou mostra a mensagem com a sessão.
        QtWidgets.QApplication.restoreOverrideCursor()
        try:
            from SAP_Gerente.modules.versionamento import client as clienteVersionamento
            from SAP_Gerente.modules.versionamento import painel
        except Exception:
            return False
        cliente = clienteVersionamento.Client(
            clienteVersionamento.service_base(self.sap.getServer()),
            token=self.sap.getToken
        )
        payload = painel.ConflictPayload({'message': erro.mensagem, 'dados': erro.dados})
        if not payload.valid:
            return False
        # O `repo_id` do 409 é onde a sessão mora (o clone no pull, o pai no
        # merge): vale ele; só sem ele a sessão é procurada no pai do clone.
        repo = payload.repo
        if not repo:
            versionamento = versionamentoDoPacote(pacote) or {}
            repo = painel.session_repository(cliente, versionamento.get('repo_id'), payload)
        dialogo = painel.ConflictDialog(
            self,
            painel.SessionResolver(cliente, repo, payload.session),
            payload,
            retryLabel='Finalizar de novo'
        )
        aceito = dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted
        if aceito:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        return aceito

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
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        dbData = self.dbCb.itemData(self.dbCb.currentIndex())
        try:
            mensagem = self.sap.endLocalMode(
                dbData,
                fieldFolder=self.getFieldFolder(),
                resolveConflict=self.resolverConflito
            )
            QtWidgets.QApplication.restoreOverrideCursor()
            # `None` é recusa já mostrada por `checkError`: nada de "sucesso".
            if mensagem is not None:
                self.showInfo('Aviso', mensagem or 'Executado com sucesso!')
        except ErroVersionamento as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Aviso', mensagemErroCampo(e))
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