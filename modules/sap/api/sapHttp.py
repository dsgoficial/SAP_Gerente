import json, requests, socket
import hashlib
import os
import re
import psycopg2
import sqlite3
from SAP_Gerente.modules.sap.factories.loginSingleton import LoginSingleton
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory
from SAP_Gerente.modules.sap.factories.dataModelFactory import DataModelFactory
from SAP_Gerente.modules.sap.postgresql import Postgresql
from SAP_Gerente.modules.sap.api.contrato import (
    PERFIL_GERENTE, MODULO_PRODUCAO,
    naoDisponivel, emAndamento, pacoteEhBaseVersionada,
    CODIGO_CONFLITO, CODIGO_NAO_EM_CAMPO, ErroVersionamento, codigoDaRecusa, versionamentoDoPacote,
    nomeArquivoCampo, pacoteParaSAPLocal
)

SSL_VERIFY=False

TIMEOUT = 60 * 2

# Contrato do SAP 3.0: as constantes estão em `contrato.py`.

class SapHttp:   

    def __init__(self, 
            qgis, 
            fmeCtrl,
            loginSingleton=LoginSingleton,
            messageFactory=UtilsFactory().createMessageFactory(),
            dataModelFactory=DataModelFactory()
        ):
        super(SapHttp, self).__init__()
        self.qgis = qgis
        self.fmeCtrl = fmeCtrl
        self.messageFactory = messageFactory
        self.activityDataModel = dataModelFactory.createDataModel('SapActivity')
        self.loginView = loginSingleton.getInstance(loginCtrl=self)
        self.server = None
        self.token = None
        self.isAdmin = False
        self.perfis = {}
        self._isReAuthenticating = False
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.verify = SSL_VERIFY

    def closeSession(self):
        if self.session:
            self.session.close()
            self.session = None

    def showErrorMessageBox(self, parent, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(parent, title, message)

    def showQuestionMessageBox(self, parent, title, message):
        questionMessageBox = self.messageFactory.createMessage('QuestionMessageBox')
        return questionMessageBox.show(parent, title, message)
    
    def showInfoMessageBox(self, parent, title, message):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(parent, title, message)

    def login(self):
        self.loginView.loadData(
            user=self.qgis.getSettingsVariable('sapmanager:user'), 
            password=self.qgis.getSettingsVariable('sapmanager:password'), 
            server=self.qgis.getSettingsVariable('sapmanager:server')
        )
        return self.loginView.showView()

    def saveLoginData(self, user, password, server):
        self.qgis.setSettingsVariable('sapmanager:user', user)
        self.qgis.setSettingsVariable('sapmanager:password', password)
        self.qgis.setSettingsVariable('sapmanager:server', server)

    def authUser(self, user, password, server):
        try:
            self.setServer(server)
            response = self.loginAdminUser(
                user, 
                password,
                self.qgis.getVersion(),
                self.qgis.getPluginsVersions()
            )
            if not response:
                return None
            
            self.setToken(response['dados']['token'])
            self.loginView.accept()
            self.saveLoginData(user, password, server)
            return True       
        except Exception as e:
            self.showErrorMessageBox(self.loginView, 'Aviso', str(e))

    def getActivityDataById(self, activityId):
        acitivityData = self.openActivity(activityId)
        acitivityData['user'] = self.qgis.getSettingsVariable('sapmanager:user')
        acitivityData['password'] = self.qgis.getSettingsVariable('sapmanager:password')
        return acitivityData

    def getNextActivityDataByUser(self, userId, nextActivity):
        acitivityData = self.openNextActivityByUser(userId, nextActivity)
        acitivityData['user'] = self.qgis.getSettingsVariable('sapmanager:user')
        acitivityData['password'] = self.qgis.getSettingsVariable('sapmanager:password')
        return acitivityData

    def getActivity(self):
        return self.activityDataModel     

    def _reAuth(self):
        user = self.qgis.getSettingsVariable('sapmanager:user')
        password = self.qgis.getSettingsVariable('sapmanager:password')
        if not (user and password):
            return False
        self._isReAuthenticating = True
        try:
            response = self.loginAdminUser(
                user,
                password,
                self.qgis.getVersion(),
                self.qgis.getPluginsVersions()
            )
            if not response:
                return False
            self.setToken(response['dados']['token'])
            return True
        except Exception:
            return False
        finally:
            self._isReAuthenticating = False

    def _requestWithRetry(self, method, url, **kwargs):
        headers = kwargs.get('headers', {}) or {}
        if self.getToken():
            headers['authorization'] = self.getToken()
        kwargs['headers'] = headers
        kwargs.setdefault('timeout', TIMEOUT)
        response = getattr(self.session, method)(url, **kwargs)
        if response.status_code == 401 and not self._isReAuthenticating and self._reAuth():
            kwargs['headers']['authorization'] = self.getToken()
            response = getattr(self.session, method)(url, **kwargs)
        if not self.checkError(response):
            return None
        return response

    def httpPost(self, url, postData, headers, timeout=TIMEOUT):
        return self._requestWithRetry('post', url, data=json.dumps(postData), headers=headers, timeout=timeout)

    def httpGet(self, url):
        return self._requestWithRetry('get', url, headers={})

    def httpPut(self, url, postData=None, headers=None, timeout=TIMEOUT):
        return self._requestWithRetry('put', url, data=json.dumps(postData or {}), headers=headers or {}, timeout=timeout)

    def httpDelete(self, url, postData=None, headers=None):
        return self._requestWithRetry('delete', url, data=json.dumps(postData or {}), headers=headers or {})

    def setServer(self, server):
        self.server = "{0}/api".format(server)

    def getServer(self):
        return self.server

    def setToken(self, token):
        self.token = token

    def getToken(self):
        return self.token

    def getProductionProfiles(self):
        response = self.httpGet(
            url="{0}/gerencia_producao/habilitacao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return [{'nome': 'Sem habilitações de produção', 'id': False}]
    
    def createProductionProfiles(self, data):
        return self._apiCreate('gerencia_producao/habilitacao', 'habilitacao', data)

    def updateProductionProfiles(self, data):
        return self._apiUpdate('gerencia_producao/habilitacao', 'habilitacao', data)

    def deleteProductionProfiles(self, data):
        return self._apiDelete('gerencia_producao/habilitacao', 'habilitacao_ids', data)

    def _usuariosDoGerente(self):
        # GET /api/usuarios é do ADMINISTRADOR no SAP 3.0. O gerente de produção
        # que não é administrador monta a lista pelas duas rotas de gerente que
        # trazem gente: quem tem habilitação (habilitacao_usuario) e quem não tem
        # (acompanhamento/usuarios_sem_perfil, só ativos). As linhas da primeira
        # não trazem `ativo` e entram como ativas.
        usuarios = {}
        for row in self._apiGet('gerencia_producao/habilitacao_usuario'):
            usuarios[row['usuario_uuid']] = row['usuario']
        for row in self._apiGet('acompanhamento/usuarios_sem_perfil'):
            usuarios[row['usuario_uuid']] = row['usuario']
        return [
            {
                'uuid': uuid,
                'nome': rotulo,
                'rotulo': rotulo,
                'ativo': True,
                'administrador': False
            }
            for uuid, rotulo in usuarios.items()
        ]

    def getUsers(self):
        # Usuário no SAP 3.0 se identifica por `uuid` (a resposta não tem `id`).
        # `rotulo` é o "posto nome de guerra" que as telas exibem.
        if self.isAdmin:
            response = self.httpGet(
                url="{0}/usuarios".format(self.getServer())
            )
            users = response.json()['dados'] if response else []
            for u in users:
                u['rotulo'] = '{0} {1}'.format(u.get('tipo_posto_grad') or '', u.get('nome_guerra') or '').strip()
        else:
            users = self._usuariosDoGerente()
        users.sort(key=lambda item: item['rotulo'])
        return users

    def getActiveUsers(self):
        return [u for u in self.getUsers() if u['ativo']]

    def loginAdminUser(self, user, password, gisVersion, pluginsVersion):
        response = self.httpPostJson(
            url="{0}/login".format(self.getServer()), 
            postData={
                "usuario" : user,
                "senha" : password,
                'plugins' : pluginsVersion,
                'qgis' : gisVersion,
                'cliente' : 'sap_fg'
            }
        )
        if not response:
            return None
        responseJson = response.json()
        if not self.validVersion(responseJson):
            raise Exception("Este plugin fala só com o SAP 3.0, e o servidor respondeu outra versão.")
        if not self.isManagerUser(responseJson):
            raise Exception("É preciso ter perfil de gerente no módulo Produção do SAP (ou ser administrador) para usar o SAP Gerente.")
        self.isAdmin = bool(responseJson['dados'].get('administrador'))
        self.perfis = responseJson['dados'].get('perfis') or {}
        return responseJson

    def validVersion(self, responseJson):
        return ('version' in responseJson and str(responseJson['version']).split('.')[0] == '3')

    def isManagerUser(self, responseJson):
        # Login do SAP 3.0 (cliente `sap_fg`): `dados.perfis` é
        # { '<nome_abrev do módulo>': perfil_id } (1 consulta, 2 operador,
        # 3 gerente). Entra o administrador global ou o gerente de `producao`.
        dados = responseJson.get('dados') or {}
        if dados.get('administrador'):
            return True
        perfis = dados.get('perfis') or {}
        return perfis.get(MODULO_PRODUCAO) == PERFIL_GERENTE

    def httpPostJson(self, url, postData, timeout=TIMEOUT):
        headers = {
            'content-type' : 'application/json'
        }
        return  self.httpPost(
            url, 
            postData,
            headers,
            timeout=timeout
        )

    def checkError(self, response):
        if response.status_code == 429:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', 'Excesso de requisições, aguarde um momento!')
            return False
        if response.status_code == 404:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', 'Servidor não encontrado!')
            return False
        if response.status_code == 413:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', 'Request Entity Too Large!')
            return False
        if response.status_code == 504:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', 'Tempo excedido!')
            return False
        if response.status_code == 401:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', 'Sessão expirada, faça o login novamente!')
            return False
        if not response.ok:
            # 403 no SAP 3.0 é falta de PERFIL (ex.: rota do acervo para quem
            # só é gerente da produção), e a mensagem do servidor diz qual.
            try:
                message = response.json()['message']
            except Exception:
                message = 'Erro {0} do servidor.'.format(response.status_code)
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
            return False
        return True

    def httpPutJson(self, url, postData, timeout=TIMEOUT):
        headers = {
            'content-type' : 'application/json'
        }
        return  self.httpPut(
            url, 
            postData,
            headers,
            timeout=timeout
        )

    def httpDeleteJson(self, url, postData):
        headers = {
            'content-type' : 'application/json'
        }
        return  self.httpDelete(
            url,
            postData,
            headers
        )

    def _apiGet(self, endpoint):
        response = self.httpGet(url="{0}/{1}".format(self.getServer(), endpoint))
        if response:
            return response.json()['dados']
        return []

    def _apiCreate(self, endpoint, key, data, timeout=TIMEOUT):
        response = self.httpPostJson(
            url="{0}/{1}".format(self.getServer(), endpoint),
            postData={key: data},
            timeout=timeout
        )
        if response:
            return response.json()['message']
        return None

    def _apiUpdate(self, endpoint, key, data, timeout=TIMEOUT):
        response = self.httpPutJson(
            url="{0}/{1}".format(self.getServer(), endpoint),
            postData={key: data},
            timeout=timeout
        )
        if response:
            return response.json()['message']
        return None

    def _apiDelete(self, endpoint, key, ids):
        response = self.httpDeleteJson(
            url="{0}/{1}".format(self.getServer(), endpoint),
            postData={key: ids}
        )
        if response:
            return response.json()['message']
        return None

    def advanceActivityToNextStep(self, activityIds, endStep):
        response = self.httpPostJson(
            url="{0}/gerencia_producao/atividade/avancar".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "concluida" : endStep
            }
        )
        if response:
            return response.json()['message']
        return None

    def createPriorityGroupActivity(self, activityIds, priority, habilitacaoId):
        # SAP 3.0: o corpo é a LISTA de atividades com UMA habilitação e UMA
        # prioridade, como na fila de uma pessoa.
        response = self.httpPostJson(
            url="{0}/gerencia_producao/fila_prioritaria_grupo".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "prioridade" : int(priority),
                "habilitacao_id" : habilitacaoId
            }
        )
        if response:
            return response.json()['message']
        return None

    def fillCommentActivity(self, activityIds, commentActivity, commentWorkspace):
        response = self.httpPutJson(
            url="{0}/gerencia_producao/observacao".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "observacao_atividade" : commentActivity,
                "observacao_unidade_trabalho" : commentWorkspace
            }
        )
        if response:
            return response.json()['message']
        return None

    def getCommentsByActivity(self, activityId):
        response = self.httpGet(
            url="{0}/gerencia_producao/atividade/{1}/observacao".format(self.getServer(), activityId)
        )
        return response.json()['dados']

    def openActivity(self, activityId):
        response = self.httpGet(
            url="{0}/gerencia_producao/atividade/{1}".format(self.getServer(), activityId),
        )
        if response:
            return response.json()
        return None

    #interface
    def openNextActivityByUser(self, userUuid, nextActivity):
        # SAP 3.0: a pessoa é o `uuid`, e não mais o id inteiro.
        params = '?proxima=true' if nextActivity else ''
        response = self.httpGet(
            url="{0}/gerencia_producao/atividade/usuario/{1}{2}".format(self.getServer(), userUuid, params)
        )
        if response:
            return response.json()
        return None
        
    #interface
    def lockWorkspace(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia_producao/unidade_trabalho/disponivel".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : False
            }
        )
        if response:
            return response.json()['message']
        return None

    # Pausar, reiniciar e voltar devolvem o ENVELOPE inteiro (`message` e
    # `dados`): `dados.revogacao` diz se o acesso ao banco de edição foi mesmo
    # fechado, e o clone da base versionada é cuidado pelo servidor. Quem chama
    # monta o texto com `contrato.mensagemComRevogacao`. `None` é falha já
    # mostrada por `checkError`.
    def _apiPostEnvelope(self, endpoint, postData, timeout=TIMEOUT):
        response = self.httpPostJson(
            url="{0}/{1}".format(self.getServer(), endpoint),
            postData=postData,
            timeout=timeout
        )
        if response:
            return response.json()
        return None

    #interface
    def pauseActivity(self, workspacesIds):
        return self._apiPostEnvelope(
            'gerencia_producao/atividade/pausar',
            {'unidade_trabalho_ids': workspacesIds}
        )

    #interface
    def restartActivity(self, workspacesIds):
        return self._apiPostEnvelope(
            'gerencia_producao/atividade/reiniciar',
            {'unidade_trabalho_ids': workspacesIds}
        )
    
    #interface
    def returnActivityToPreviousStep(self, activityIds, preserveUser):
        return self._apiPostEnvelope(
            'gerencia_producao/atividade/voltar',
            {
                "atividade_ids" : activityIds,
                "manter_usuarios" : preserveUser
            }
        )

    #interface
    def setPriorityActivity(self, activityIds, priority, userUuid):
        fila = {
            "atividade_ids" : activityIds,
            "prioridade" : int(priority),
            "usuario_uuid" : userUuid
        }

        response = self.httpPostJson(
            url="{0}/gerencia_producao/fila_prioritaria".format(self.getServer()),
            postData=fila
        )
        if response:
            return response.json()['message']
        return None

     #interface
    def unlockWorkspace(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia_producao/unidade_trabalho/disponivel".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : True
            }
        )
        if response:
            return response.json()['message']
        return None

    def getStyles(self):
        return self._apiGet('producao/estilos')

    def getGroupStyles(self):
        return self._apiGet('producao/grupo_estilos')

    def createGroupStyles(self, data):
        return self._apiCreate('producao/grupo_estilos', 'grupo_estilos', data)

    def deleteGroupStyles(self, data):
        return self._apiDelete('producao/grupo_estilos', 'grupo_estilos_ids', data)

    def updateGroupStyles(self, data):
        return self._apiUpdate('producao/grupo_estilos', 'grupo_estilos', data)

    def getStyleNames(self):
        return self._apiGet('producao/estilos')

    def createStyles(self, data):
        return self._apiCreate('producao/estilos', 'estilos', data)

    def updateStyles(self, data):
        return self._apiUpdate('producao/estilos', 'estilos', data)

    def deleteStyles(self, ids):
        return self._apiDelete('producao/estilos', 'estilos_ids', ids)

    def getModels(self):
        return self._apiGet('producao/modelos')

    def createModels(self, data):
        return self._apiCreate('producao/modelos', 'modelos', data)

    def updateModels(self, data):
        return self._apiUpdate('producao/modelos', 'modelos', data)

    def deleteModels(self, ids):
        return self._apiDelete('producao/modelos', 'modelos_ids', ids)

    def getRules(self):
        return self._apiGet('producao/regras')

    def createRules(self, data):
        return self._apiCreate('producao/regras', 'regras', data)

    def updateRules(self, data):
        return self._apiUpdate('producao/regras', 'regras', data)

    def deleteRules(self, ids):
        return self._apiDelete('producao/regras', 'regras_ids', ids)

    # O GRUPO DE REGRAS não existe no SAP 3.0 (nem no 2.3.6): a regra é
    # `{nome, regra}` em /producao/regras.
    def getRuleSet(self):
        naoDisponivel('o grupo de regras não existe no SAP 3.0; as regras são cadastradas direto em "Gerenciador de Regras".')

    def createRuleSet(self, data):
        naoDisponivel('o grupo de regras não existe no SAP 3.0.')

    def updateRuleSet(self, data):
        naoDisponivel('o grupo de regras não existe no SAP 3.0.')

    def deleteRuleSet(self, ids):
        naoDisponivel('o grupo de regras não existe no SAP 3.0.')
    
    def getLayersQgisProject(self, projectInProgress, block, lotInProgress):
        # Construir os parâmetros da query
        params = []
        
        if projectInProgress:
            params.append('em_andamento_projeto=true')
            
        if lotInProgress:
            params.append('em_andamento_lote=true')
            
        if block:
            params.append(f'bloco={block["id"]}')
        
        # Juntar os parâmetros com &
        query_string = '?' + '&'.join(params) if params else ''
        
        response = self.httpGet(
            url="{0}/gerencia_producao/view_acompanhamento{1}".format(self.getServer(), query_string)
        )
        
        if response:
            return response.json()['dados']
        return []

    # No SAP 3.0 o usuário é da PLATAFORMA (dgeo.usuario) e não há serviço de
    # autenticação externo: quem cria e edita conta é o administrador, na tela
    # Usuários do SAP.
    def deleteActivities(self, activityIds):
        return self._apiDelete('producao/atividades', 'atividades_ids', activityIds)
    
    def createActivities(self, data):
        response = self.httpPostJson(
            url="{0}/producao/atividades".format(self.getServer()),
            postData=data    
        )
        if response:
            return response.json()['message']
        return None

    def getDatabases(self):
        return self._apiGet('producao/banco_dados')

    def getAuthDatabase(self):
        return self._apiGet('producao/login')

    def resetPrivileges(self):
        response = self.httpPut(
            url="{0}/gerencia_producao/atividades/permissoes".format(self.getServer()),
            timeout=60*5
        )
        if response:
            return response.json()['message']
        return None

    def importLayers(self, layersImported):
        return self._apiCreate('producao/configuracao/camadas', 'camadas', layersImported)

    def getLayers(self):
        return self._apiGet('producao/configuracao/camadas')

    def getLayersProductionLines(self):
        return self._apiGet('producao/configuracao/camadas/linha_producao')

    def deleteLayers(self, layersIds):
        return self._apiDelete('producao/configuracao/camadas', 'camadas_ids', layersIds)

    def updateLayers(self, layersData):
        return self._apiUpdate('producao/configuracao/camadas', 'camadas', layersData)

    # O LOTE é do ACERVO no SAP 3.0 (acervo.lote), e se cadastra na tela do Acervo,
    # nunca aqui. O seletor vem de GET /api/gerencia_producao/lotes (desde a 3.31.0):
    # todo lote, inclusive o que ainda não tem unidade de trabalho, para quem é
    # gerente da produção, sem exigir perfil no Acervo. "Em execução" do SAP
    # 2.3.5 é "não encerrado", e o lote desativado no Acervo sai da escolha.
    def getLots(self):
        return [l for l in self.getAllLots() if emAndamento(l) and l.get('ativo', True)]

    def getAllLots(self):
        return self._apiGet('gerencia_producao/lotes')

    def alterBlock(self, workspacesIds, lotId):
        response = self.httpPutJson(
            url="{0}/producao/unidade_trabalho/bloco".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'bloco_id': lotId
            }    
        )
        if response:
            return response.json()['message']
        return None

    def revokePrivileges(self, dadoProducaoId):
        # SAP 3.0: o banco é identificado pelo dado de produção.
        response = self.httpPostJson(
            url="{0}/gerencia_producao/banco_dados/revogar_permissoes".format(self.getServer()),
            postData={
                "dado_producao_id" : dadoProducaoId
            }
        )
        if response:
            return response.json()['message']
        return None

    def getFmeServers(self):
        return self._apiGet('producao/configuracao/gerenciador_fme')

    def createFmeServers(self, fmeServers):
        return self._apiCreate('producao/configuracao/gerenciador_fme', 'gerenciador_fme', fmeServers)

    def updateFmeServers(self, fmeServers):
        return self._apiUpdate('producao/configuracao/gerenciador_fme', 'gerenciador_fme', fmeServers)

    def deleteFmeServers(self, fmeServersIds):
        return self._apiDelete('producao/configuracao/gerenciador_fme', 'servidores_id', fmeServersIds)

    def getFmeProfiles(self):
        return self._apiGet('producao/configuracao/perfil_fme')

    def createFmeProfiles(self, fmeProfiles):
        return self._apiCreate('producao/configuracao/perfil_fme', 'perfis_fme', fmeProfiles)

    def updateFmeProfiles(self, fmeProfiles):
        return self._apiUpdate('producao/configuracao/perfil_fme', 'perfis_fme', fmeProfiles)

    def deleteFmeProfiles(self, fmeProfilesIds):
        return self._apiDelete('producao/configuracao/perfil_fme', 'perfil_fme_ids', fmeProfilesIds)
    
    def getPhases(self):
        return self._apiGet('producao/fases')

    def getSubphases(self):
        return self._apiGet('producao/subfases')

    def getActiveSubphases(self):
        return self._apiGet('producao/subfases?status=ativo')

    def getSteps(self):
        return self._apiGet('producao/etapas')

    def deleteUserActivities(self, userUuid):
        # SAP 3.0: a confirmação é repetir o uuid da pessoa no corpo, e as
        # atividades FINALIZADAS não são tocadas.
        response = self.httpDeleteJson(
            url="{0}/perigo/atividades/usuario/{1}".format(self.getServer(), userUuid),
            postData={
                'confirmar': userUuid
            }
        )
        if response:
            return response.json()['message']
        return []

    def getInputTypes(self):
        return self._apiGet('producao/tipo_insumo')

    def getAllInputGroups(self):
        return self._apiGet('producao/grupo_insumo')

    def getInputGroups(self):
        return self._apiGet('producao/grupo_insumo?disponivel=true')

    def createInputGroups(self, inputGroups):
        return self._apiCreate('producao/grupo_insumo', 'grupo_insumos', inputGroups)

    def updateInputGroups(self, inputGroups):
        return self._apiUpdate('producao/grupo_insumo', 'grupo_insumos', inputGroups)

    def deleteInputGroups(self, inputGroupIds):
        return self._apiDelete('producao/grupo_insumo', 'grupo_insumos_ids', inputGroupIds)

    def getInsumos(self, grupoInsumoId=None, tipoInsumoCode=None):
        params = []
        if grupoInsumoId is not None:
            params.append('grupo_insumo_id={0}'.format(int(grupoInsumoId)))
        if tipoInsumoCode is not None:
            params.append('tipo_insumo_id={0}'.format(tipoInsumoCode))
        query = '?' + '&'.join(params) if params else ''
        return self._apiGet('producao/insumo' + query)

    def updateInsumos(self, insumos):
        return self._apiUpdate('producao/insumo', 'insumos', insumos)

    def deleteInsumos(self, insumoIds):
        return self._apiDelete('producao/insumo', 'insumo_ids', insumoIds)

    def getInsumosPorUT(self, unidadeTrabalhoId):
        return self._apiGet('producao/unidade_trabalho/insumos?unidade_trabalho_id={0}'.format(unidadeTrabalhoId))

    def deleteAssociatedInputs(self, workspacesIds, inputGroupId):
        response = self.httpDeleteJson(
            url="{0}/producao/unidade_trabalho/insumos".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'grupo_insumo_id': inputGroupId
            }  
        )
        if response:
            return response.json()['message']
        return None

    def deleteWorkUnits(self, workspacesIds):
        return self._apiDelete('producao/unidade_trabalho', 'unidade_trabalho_ids', workspacesIds)

    def getProductionLines(self):
        def sortByName(elem):
            return elem['linha_producao']
        response = self.httpGet(
            url="{0}/producao/linha_producao".format(self.getServer())
        )
        if response:
            productionLines = response.json()['dados']
            productionLines.sort(key=sortByName)
            return productionLines
        return []

    def getActiveProductionLines(self):
        def sortByName(elem):
            return elem['linha_producao']
        response = self.httpGet(
            url="{0}/producao/linha_producao?status=ativo".format(self.getServer())
        )
        if response:
            productionLines = response.json()['dados']
            productionLines.sort(key=sortByName)
            return productionLines
        return []

    def createInputs(self, inputGroupCode, inputGroupId, inputs):
        response = self.httpPostJson(
            url="{0}/producao/insumo".format(self.getServer()),
            postData={
                'tipo_insumo_id': inputGroupCode,
                'grupo_insumo_id': inputGroupId,
                'insumos': inputs
            }
        )
        if response:
            return response.json()['message']
        return None

    def getRoutines(self):
        return self._apiGet('producao/tipo_rotina')

    def getAssociationStrategies(self):
        return self._apiGet('producao/tipo_estrategia_associacao')

    def associateInputs(self, workspacesIds, inputGroupId, associationStrategyId, defaultPath):
        response = self.httpPostJson(
            url="{0}/producao/unidade_trabalho/insumos".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'grupo_insumo_id': inputGroupId,
                'estrategia_id': associationStrategyId,
                'caminho_padrao': defaultPath
            }   
        )
        if response:
            return response.json()['message']
        return None

    def loadWorkUnit(self, lotId, subphaseIds, workUnits):
        response = self.httpPostJson(
            url="{0}/producao/unidade_trabalho".format(self.getServer()),
            postData={
                'lote_id': lotId,
                'subfase_ids': subphaseIds,
                'unidades_trabalho': workUnits
            }   
        )
        if response:
            return response.json()['message']
        return None

    def getProductionData(self):
        return self._apiGet('producao/dado_producao')

    def getProductionDataType(self):
        return self._apiGet('producao/tipo_dado_producao')

    def copyWorkUnit(self, workspacesIds, stepsIds, associateInputs):
        response = self.httpPostJson(
            url="{0}/producao/unidade_trabalho/copiar".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'subfase_ids': stepsIds,
                'associar_insumos': associateInputs
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def getModelProfiles(self):
        return self._apiGet('producao/configuracao/perfil_modelo')

    def createModelProfiles(self, data):
        return self._apiCreate('producao/configuracao/perfil_modelo', 'perfis_modelo', data)

    def updateModelProfiles(self, data):
        return self._apiUpdate('producao/configuracao/perfil_modelo', 'perfis_modelo', data)

    def deleteModelProfiles(self, ids):
        return self._apiDelete('producao/configuracao/perfil_modelo', 'perfil_modelo_ids', ids)

    def getRuleProfiles(self):
        return self._apiGet('producao/configuracao/perfil_regras')

    def createRuleProfiles(self, data):
        return self._apiCreate('producao/configuracao/perfil_regras', 'perfis_regras', data)

    def updateLinhaProducao(self, data):
        return self._apiUpdate('producao/linha_producao', 'linhas_producao', data)

    def updateRuleProfiles(self, data):
        return self._apiUpdate('producao/configuracao/perfil_regras', 'perfis_regras', data)

    def deleteRuleProfiles(self, ids):
        return self._apiDelete('producao/configuracao/perfil_regras', 'perfil_regras_ids', ids)

    def getStyleProfiles(self):
        return self._apiGet('producao/configuracao/perfil_estilos')

    def createStyleProfiles(self, data):
        return self._apiCreate('producao/configuracao/perfil_estilos', 'perfis_estilos', data)

    def updateStyleProfiles(self, data):
        return self._apiUpdate('producao/configuracao/perfil_estilos', 'perfis_estilos', data)

    def deleteStyleProfiles(self, ids):
        return self._apiDelete('producao/configuracao/perfil_estilos', 'perfil_estilos_ids', ids)

    # O PROJETO é do ACERVO no SAP 3.0 (acervo.projeto), e se cadastra na tela do
    # Acervo. O seletor vem do quadro de projetos do acompanhamento (consulta em
    # `producao`), que traz todo projeto, com os nomes de campo de antes.
    # "Em execução" do SAP 2.3.5 é "não encerrado".
    def getProjects(self):
        return [p for p in self.getAllProjects() if emAndamento(p)]

    def getAllProjects(self):
        return [
            {
                'id': p['projeto_id'],
                'nome': p['projeto'],
                'descricao': p['descricao'],
                'data_inicio': p['data_inicio'],
                'data_fim': p['data_fim'],
                'status_execucao_id': p['status_execucao_id'],
                'status_execucao': p['status']
            }
            for p in self._apiGet('acompanhamento/projetos')
        ]

    def getStepType(self):
        return self._apiGet('producao/tipo_etapa')

    # Os padrões de "Criar Etapas Padrão" (`dominio.tipo_controle_qualidade`).
    # Lidos do servidor para que o padrão que ele acrescentar (por exemplo, com a
    # etapa 6 'Integração') apareça sem mudar o plugin.
    def getQualityControlTypes(self):
        return self._apiGet('producao/tipo_controle_qualidade')

    def getProfileProductionStep(self):
        return self._apiGet('gerencia_producao/habilitacao_etapa')

    def createProfileProductionStep(self, data):
        return self._apiCreate('gerencia_producao/habilitacao_etapa', 'habilitacao_etapa', data)

    def updateProfileProductionStep(self, data):
        return self._apiUpdate('gerencia_producao/habilitacao_etapa', 'habilitacao_etapa', data)

    def deleteProfileProductionStep(self, data):
        return self._apiDelete('gerencia_producao/habilitacao_etapa', 'habilitacao_etapa_ids', data)

    def getUserProfileProduction(self):
        return self._apiGet('gerencia_producao/habilitacao_usuario')

    def createUserProfileProduction(self, data):
        return self._apiCreate('gerencia_producao/habilitacao_usuario', 'habilitacao_usuario', data)

    def updateUserProfileProduction(self, data):
        return self._apiUpdate('gerencia_producao/habilitacao_usuario', 'habilitacao_usuario', data)

    def deleteUserProfileProduction(self, data):
        return self._apiDelete('gerencia_producao/habilitacao_usuario', 'habilitacao_usuario_ids', data)

    def getUserBlocks(self):
        return self._apiGet('gerencia_producao/habilitacao_bloco')

    def createUserBlockProduction(self, data):
        return self._apiCreate('gerencia_producao/habilitacao_bloco', 'habilitacao_bloco', data)

    def updateUserBlockProduction(self, data):
        return self._apiUpdate('gerencia_producao/habilitacao_bloco', 'habilitacao_bloco', data)

    def deleteUserBlockProduction(self, data):
        return self._apiDelete('gerencia_producao/habilitacao_bloco', 'habilitacao_bloco_ids', data)

    def getBlocks(self):
        return self._apiGet('producao/bloco?status=execucao')

    def getAllBlocks(self):
        return self._apiGet('producao/bloco')

    def createMenus(self, data):
        return self._apiCreate('producao/menus', 'menus', data)

    def updateMenus(self, data):
        return self._apiUpdate('producao/menus', 'menus', data)

    def deleteMenus(self, data):
        return self._apiDelete('producao/menus', 'menus_ids', data)

    def getMenus(self):
        return self._apiGet('producao/menus')

    def getMenuProfiles(self):
        return self._apiGet('producao/configuracao/perfil_menu')

    def createMenuProfiles(self, data):
        return self._apiCreate('producao/configuracao/perfil_menu', 'perfis_menu', data)

    def updateMenuProfiles(self, data):
        return self._apiUpdate('producao/configuracao/perfil_menu', 'perfis_menu', data)

    def deleteMenuProfiles(self, data):
        return self._apiDelete('producao/configuracao/perfil_menu', 'perfil_menu_ids', data)

    def createAllActivities(self, data):
        response = self.httpPostJson(
            url="{0}/producao/atividades/todas".format(self.getServer()),
            postData=data,
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def createDefaultStep(self, padraoCq, phaseId, lotId):
        response = self.httpPostJson(
            url="{0}/producao/etapas/padrao".format(self.getServer()),
            postData={
                'tipo_controle_qualidade_id': padraoCq,
                'fase_id': phaseId,
                'lote_id': lotId,
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def deleteWorkUnitActivities(self, workUnitIds):
        return self._apiDelete('producao/unidade_trabalho/atividades', 'unidade_trabalho_ids', workUnitIds)

    def updateLayersQgisProject(self):
        response = self.httpPut(
            url="{0}/gerencia_producao/refresh_views".format(self.getServer())
        )
        if response:
            return response.json()['message']
        return None

    # Projeto e lote do ACERVO: POST e PUT recebem UM objeto por vez (e não
    # uma lista sob uma chave), por isso o laço. A rota cobra perfil no módulo
    # Acervo (operador para criar e editar, gerente para apagar).
    def createBlocks(self, data):
        return self._apiCreate('producao/bloco', 'blocos', data)

    def deleteBlocks(self, data):
        return self._apiDelete('producao/bloco', 'bloco_ids', data)

    def updateBlocks(self, data):
        return self._apiUpdate('producao/bloco', 'blocos', data)

    def createProductionData(self, data):
        return self._apiCreate('producao/dado_producao', 'dado_producao', data)

    def deleteProductionData(self, data):
        return self._apiDelete('producao/dado_producao', 'dado_producao_ids', data)

    def updateProductionData(self, data):
        return self._apiUpdate('producao/dado_producao', 'dado_producao', data)

    def createBlockInputs(self, data):
        response = self.httpPostJson(
            url="{0}/producao/bloco/insumos".format(self.getServer()),
            postData=data
        )
        if response:
            return response.json()['message']
        return None

    def revokeUserPrivileges(self, data):
        response = self.httpPostJson(
            url="{0}/gerencia_producao/banco_dados/revogar_permissoes_usuario".format(self.getServer()),
            postData=data
        )
        if response:
            return response.json()['message']
        return None

    def getQgisVersion(self):
        return self._apiGet('gerencia_producao/versao_qgis')

    def updateQgisVersion(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia_producao/versao_qgis".format(self.getServer()),
            postData=data
        )
        if response:
            return response.json()['message']
        return None

    def getProfileFinalization(self):
        return self._apiGet('producao/configuracao/perfil_requisito_finalizacao')

    def updateProfileFinalization(self, data):
        return self._apiUpdate('producao/configuracao/perfil_requisito_finalizacao', 'perfis_requisito', data)

    def createProfileFinalization(self, data):
        return self._apiCreate('producao/configuracao/perfil_requisito_finalizacao', 'perfis_requisito', data)

    def deleteProfileFinalization(self, data):
        return self._apiDelete('producao/configuracao/perfil_requisito_finalizacao', 'perfil_requisito_ids', data)

    def getAlias(self):
        return self._apiGet('producao/alias')

    def updateAlias(self, data):
        return self._apiUpdate('producao/alias', 'alias', data)

    def createAlias(self, data):
        return self._apiCreate('producao/alias', 'alias', data)

    def deleteAlias(self, data):
        return self._apiDelete('producao/alias', 'alias_ids', data)

    def getAliasProfile(self):
        return self._apiGet('producao/configuracao/perfil_alias')

    def updateAliasProfile(self, data):
        return self._apiUpdate('producao/configuracao/perfil_alias', 'perfis_alias', data)

    def createAliasProfile(self, data):
        return self._apiCreate('producao/configuracao/perfil_alias', 'perfis_alias', data)

    def deleteAliasProfile(self, data):
        return self._apiDelete('producao/configuracao/perfil_alias', 'perfis_alias_ids', data)

    def getPlugins(self):
        return self._apiGet('gerencia_producao/plugins')

    def updatePlugins(self, data):
        return self._apiUpdate('gerencia_producao/plugins', 'plugins', data)

    def createPlugins(self, data):
        return self._apiCreate('gerencia_producao/plugins', 'plugins', data)

    def deletePlugins(self, data):
        return self._apiDelete('gerencia_producao/plugins', 'plugins_ids', data)

    def getShortcuts(self):
        return self._apiGet('gerencia_producao/atalhos')

    def updateShortcuts(self, data):
        return self._apiUpdate('gerencia_producao/atalhos', 'atalhos', data)

    def createShortcuts(self, data):
        return self._apiCreate('gerencia_producao/atalhos', 'atalhos', data)

    def deleteShortcuts(self, data):
        return self._apiDelete('gerencia_producao/atalhos', 'atalhos_ids', data)

    def getStatusDomain(self):
        return self._apiGet('producao/status')

    def getShowTypes(self):
        return self._apiGet('producao/tipo_exibicao')

    def getLineages(self):
        return self._apiGet('producao/configuracao/perfil_linhagem')

    def updateLineages(self, data):
        return self._apiUpdate('producao/configuracao/perfil_linhagem', 'perfis_linhagem', data)

    def createLineages(self, data):
        return self._apiCreate('producao/configuracao/perfil_linhagem', 'perfis_linhagem', data)

    def deleteLineages(self, data):
        return self._apiDelete('producao/configuracao/perfil_linhagem', 'perfil_linhagem_ids', data)

    def getProblemActivity(self):
        return self._apiGet('gerencia_producao/problema_atividade')

    def updateProblemActivity(self, data):
        return self._apiUpdate('gerencia_producao/problema_atividade', 'problema_atividade', data)

    def getThemes(self):
        return self._apiGet('producao/temas')

    def updateThemes(self, data):
        return self._apiUpdate('producao/temas', 'temas', data)

    def createThemes(self, data):
        return self._apiCreate('producao/temas', 'temas', data)

    def deleteThemes(self, data):
        return self._apiDelete('producao/temas', 'temas_ids', data)

    def getThemesProfile(self):
        return self._apiGet('producao/configuracao/perfil_temas')

    def updateThemesProfile(self, data):
        return self._apiUpdate('producao/configuracao/perfil_temas', 'perfis_temas', data)

    def createThemesProfile(self, data):
        return self._apiCreate('producao/configuracao/perfil_temas', 'perfis_temas', data)

    def deleteThemesProfile(self, data):
        return self._apiDelete('producao/configuracao/perfil_temas', 'perfil_temas_ids', data)

    def getHiddenColumns(self):
        return self._apiGet('producao/colunas_ocultas')

    def updateHiddenColumns(self, data):
        return self._apiUpdate('producao/colunas_ocultas', 'colunas_ocultas', data)

    def createHiddenColumns(self, data):
        return self._apiCreate('producao/colunas_ocultas', 'colunas_ocultas', data)

    def deleteHiddenColumns(self, data):
        return self._apiDelete('producao/colunas_ocultas', 'colunas_ocultas_ids', data)

    def getHiddenColumnsProfile(self):
        return self._apiGet('producao/configuracao/perfil_colunas_ocultas')

    def updateHiddenColumnsProfile(self, data):
        return self._apiUpdate('producao/configuracao/perfil_colunas_ocultas', 'perfis_colunas_ocultas', data)

    def createHiddenColumnsProfile(self, data):
        return self._apiCreate('producao/configuracao/perfil_colunas_ocultas', 'perfis_colunas_ocultas', data)

    def deleteHiddenColumnsProfile(self, data):
        return self._apiDelete('producao/configuracao/perfil_colunas_ocultas', 'perfil_colunas_ocultas_ids', data)

    def getLastCompletedActivities(self):
        return self._apiGet('acompanhamento/ultimas_atividades_finalizadas')

    def getRunningActivities(self):
        return self._apiGet('acompanhamento/atividades_em_execucao')

    def reshapeUT(self, workspacesId, reshapeGeom):
        response = self.httpPutJson(
            url="{0}/producao/unidade_trabalho/reshape".format(self.getServer()),
            postData={
                'unidade_trabalho_id': workspacesId,
                'reshape_geom': reshapeGeom
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def cutUT(self, workspacesId, cutGeoms):
        response = self.httpPutJson(
            url="{0}/producao/unidade_trabalho/cut".format(self.getServer()),
            postData={
                'unidade_trabalho_id': workspacesId,
                'cut_geoms': cutGeoms
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def mergeUT(self, workspacesIds, mergeGeom):
        response = self.httpPutJson(
            url="{0}/producao/unidade_trabalho/merge".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'merge_geom': mergeGeom
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def startLocalMode(self, activityId):
        # SAP 3.0: a atividade é iniciada em nome de quem chama (o gerente); quem
        # executou de fato vai no `finalizar_modo_local`.
        response = self.httpPutJson(
            url="{0}/gerencia_producao/iniciar_modo_local".format(self.getServer()),
            postData={
                'atividade_id': activityId
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def _conexaoSAPLocal(self, dbData):
        return Postgresql(
            dbData['database'],
            dbData['username'],
            dbData['host'],
            dbData['port'],
            dbData['password']
        )

    def checkSAPLocalDatabase(self, dbData):
        # O banco local tem de ter `public.sap_local` vazia. Conferido ANTES de
        # `iniciar_modo_local`, que muda a atividade no servidor: banco local
        # recusado depois dele deixava a atividade em modo local sem pacote.
        pg = self._conexaoSAPLocal(dbData)
        try:
            pg.execute(
                '''
                    SELECT * FROM public.sap_local;
                ''',
                ()
            )
        except psycopg2.errors.UndefinedTable:
            raise Exception('Tabela "public.sap_local" não existe!')
        result = pg.execute(
            '''
                SELECT count(*) FROM public.sap_local;
            ''',
            ()
        )
        if result[0][0] != 0:
            raise Exception('Há dados na tabela "public.sap_local"!')
        return pg

    def exportToSAPLocal(self, activityData):
        pg = self.checkSAPLocalDatabase(activityData['local_db'])
        # O pacote vai SEM segredo (`contrato.pacoteParaSAPLocal`): nem a senha
        # do gerente no SAP nem a do banco local ficam gravadas no banco local.
        pacote = pacoteParaSAPLocal(activityData)
        pg.execute(
            '''
                INSERT INTO public.sap_local (
                        atividade_id,
                        json_atividade,
                        geom
                    )
                    VALUES (
                        %s,
                        %s,
                        ST_Transform(ST_GeomFromEWKT(%s), 4326)
                    )
                    RETURNING *;
            ''',
            (
                pacote['dados']['atividade']['id'],
                json.dumps(pacote),
                pacote['dados']['atividade']['geom']
            )
        )

    def validDBEndLocalMode(
            self,
            database,
            host,
            port,
            username,
            password
        ):
        try:
            pg = Postgresql(
                database,
                username,
                host,
                port,
                password
            )
            result = pg.execute(
                '''
                    SELECT count(*) FROM public.sap_local;
                ''',
                ()
            )
            if result[0][0] == 0:
                return False
            result = pg.execute(
                '''
                    SELECT
                        EXTRACT (EPOCH FROM data_inicio),
                        EXTRACT (EPOCH FROM data_fim),
                        nome_usuario,
                        usuario_uuid
                    FROM public.sap_local;
                ''',
                ()
            )
            if len([ d for d in result[0] if d is None]) > 0:
                return False
            return True
        except Exception:
            return False

    def readSAPLocal(self, pg):
        result = pg.execute(
            '''
                SELECT
                    atividade_id,
                    data_inicio::text,
                    data_fim::text,
                    usuario_uuid,
                    json_atividade
                FROM public.sap_local;
            ''',
            ()
        )
        result = result[0]
        pacote = result[4]
        if isinstance(pacote, str):
            try:
                pacote = json.loads(pacote)
            except ValueError:
                pacote = None
        return {
            'corpo': {
                'atividade_id': result[0],
                'data_inicio': result[1],
                'data_fim': result[2],
                'usuario_uuid': result[3]
            },
            'pacote': pacote if isinstance(pacote, dict) else {}
        }

    def endLocalMode(self, dbData, fieldFolder=None, resolveConflict=None):
        # Base versionada (tipo 4, contrato 9.2 e 9.4): o arquivo de campo volta
        # ao servidor ANTES de `finalizar_modo_local`. `resolveConflict(erro,
        # pacote)` abre a resolução do 409 de conflito e diz se vale finalizar
        # de novo; sem ela, ou recusada, o 409 sobe como `ErroVersionamento`.
        pg = self._conexaoSAPLocal(dbData)
        registro = self.readSAPLocal(pg)
        if not pacoteEhBaseVersionada(registro['pacote']):
            response = self.httpPutJson(
                url="{0}/gerencia_producao/finalizar_modo_local".format(self.getServer()),
                postData=registro['corpo'],
                timeout=TIMEOUT
            )
            if response:
                return response.json()['message']
            return None
        self._returnFieldFile(pg, registro, fieldFolder)
        while True:
            try:
                return self.finishLocalModeVersioned(registro['corpo'])
            except ErroVersionamento as erro:
                if (
                        erro.codigo == CODIGO_CONFLITO
                        and resolveConflict
                        and resolveConflict(erro, registro['pacote'])
                    ):
                    continue
                raise

    def _returnFieldFile(self, pg, registro, fieldFolder):
        pacote = registro['pacote']
        versionamento = versionamentoDoPacote(pacote) or {}
        nome = versionamento.get('arquivo')
        if not nome or os.path.basename(nome) != nome:
            raise Exception(
                'O pacote do banco local não diz o arquivo de campo (versionamento.arquivo): '
                'ele não foi configurado por esta versão do SAP Gerente.'
            )
        if not fieldFolder:
            raise Exception('Escolha a pasta do arquivo de campo ({0}).'.format(nome))
        caminho = os.path.join(fieldFolder, nome)
        if not os.path.isfile(caminho):
            raise Exception('O arquivo de campo {0} não está na pasta escolhida.'.format(nome))
        # O que o QGIS editou e não passou pelo checkpoint está no `-wal`: sem
        # consolidar, o arquivo que sobe não leva essas edições.
        self._consolidarWal(caminho, nome)
        # A identidade lida antes do SHA-256: ler o arquivo pelo SQLite não pode
        # mudar os bytes que sobem depois.
        identidade = self._identidadeCampo(caminho)
        # O SHA-256 é o do arquivo que sobe, calculado agora. O `sha256` do
        # pacote é o do download e não confere depois de o QGIS abrir o arquivo
        # (abrir já muda os bytes); o `<arquivo>.sap-conferido.json` que o SAP
        # Operador grava ao lado não é lido nem enviado.
        sha256 = self._sha256(caminho)
        # Uma devolução anterior que o servidor não confirmou por inteiro: a
        # finalização para sempre com o mesmo motivo, nunca calada.
        if versionamento.get('enviado_divergente'):
            raise ErroVersionamento(versionamento['enviado_divergente'])
        # Reenvio do MESMO arquivo (finalização anterior parou num conflito
        # depois de devolver o campo): o servidor já o tem e já limpou o
        # `em_campo`, então só a finalização se repete.
        if versionamento.get('enviado_sha256') == sha256:
            return
        # Já devolvido, e os bytes mudaram (o arquivo foi reaberto no QGIS, que
        # muda os bytes só de abrir): vale a identidade do repositório, não os
        # bytes. Sem edição capturada depois da devolução, o servidor tem tudo e
        # só a finalização se repete; com edição nova, para com o motivo.
        if versionamento.get('enviado_sha256') and 'enviado_seq' in versionamento:
            self._conferirJaDevolvido(nome, versionamento, identidade)
            return
        repoId = versionamento.get('repo_id')
        if identidade and repoId and identidade['repo_id'] != repoId:
            raise ErroVersionamento(
                'O arquivo de campo {0} é do repositório {1}, e esta atividade é do repositório {2}. '
                'Nada foi enviado nem finalizado.'.format(nome, identidade['repo_id'], repoId)
            )
        try:
            resposta = self.uploadFieldFile(registro['corpo']['atividade_id'], caminho)
        except ErroVersionamento as erro:
            if erro.codigo != CODIGO_NAO_EM_CAMPO:
                raise
            # O clone já saiu de campo: um arquivo já voltou ao servidor (a
            # marca local se perdeu, ou a devolução foi por outro caminho). Se
            # a marca diz que voltou OUTRO arquivo, este foi editado depois, e
            # as edições novas não entram: para, em vez de finalizar calado.
            if versionamento.get('enviado_sha256'):
                raise ErroVersionamento(
                    'O arquivo de campo {0} mudou depois de devolvido ao servidor, que já tem a '
                    'versão anterior e não aceita outra. Nada foi finalizado.'.format(nome),
                    status=erro.status, codigo=erro.codigo, dados=erro.dados
                )
            return
        versionamento['enviado_sha256'] = sha256
        divergencia = None
        if identidade:
            # O que a devolução prova: o servidor relê o clone que recebeu e
            # responde `repo_id` e `pending_versions` (as versões capturadas a
            # registrar). Têm de ser as do arquivo: menos versões no servidor
            # seria edição de campo perdida no caminho.
            versionamento['enviado_repo_id'] = identidade['repo_id']
            versionamento['enviado_seq'] = identidade['seq']
            dados = (resposta or {}).get('dados') if isinstance(resposta, dict) else None
            dados = dados if isinstance(dados, dict) else {}
            servidorRepo = dados.get('repo_id')
            servidorPendentes = dados.get('pending_versions')
            if servidorRepo is not None and servidorRepo != identidade['repo_id']:
                divergencia = 'o servidor respondeu o repositório {0}, e o arquivo é do {1}'.format(
                    servidorRepo, identidade['repo_id'])
            elif isinstance(servidorPendentes, int) and servidorPendentes != identidade['pendentes']:
                divergencia = 'o servidor tem {0} versão(ões) capturada(s) a registrar, e o arquivo tem {1}'.format(
                    servidorPendentes, identidade['pendentes'])
            if divergencia:
                divergencia = (
                    'A devolução do arquivo de campo {0} não confere com o que o servidor recebeu: {1}. '
                    'A atividade não foi finalizada, para nenhuma edição de campo sumir em silêncio; '
                    'verifique o clone da atividade no servidor antes de finalizar.'
                ).format(nome, divergencia)
                versionamento['enviado_divergente'] = divergencia
        pg.execute(
            '''
                UPDATE public.sap_local SET json_atividade = %s RETURNING atividade_id;
            ''',
            (json.dumps(pacote),)
        )
        if divergencia:
            raise ErroVersionamento(divergencia)

    @staticmethod
    def _identidadeCampo(caminho):
        # A identidade do GeoPackage de campo como repositório do versionamento
        # (`dsg_meta`: `family`, `repo_id`, `parent_id`) e o contador das
        # versões capturadas (`dsg_seq.last`, que só a captura de uma edição faz
        # andar), com as pendentes de registro (`dsg_seq.last` menos o maior
        # `seq_last` das revisões, como o serviço as conta). None quando o
        # arquivo não é um repositório do versionamento legível.
        try:
            conexao = sqlite3.connect(caminho, timeout=2)
            try:
                meta = dict(conexao.execute('SELECT key, value FROM dsg_meta').fetchall())
                seq = conexao.execute('SELECT last FROM dsg_seq WHERE k = 1').fetchone()
                feito = conexao.execute(
                    'SELECT coalesce(max(seq_last), 0) FROM dsg_revisions WHERE seq_last IS NOT NULL'
                ).fetchone()
            finally:
                conexao.close()
        except sqlite3.Error:
            return None
        if meta.get('family') != 'dsg-versioning' or not meta.get('repo_id') or not seq:
            return None
        return {
            'repo_id': meta['repo_id'],
            'parent_id': meta.get('parent_id'),
            'seq': int(seq[0]),
            'pendentes': int(seq[0]) - int(feito[0] if feito else 0)
        }

    @staticmethod
    def _conferirJaDevolvido(nome, versionamento, identidade):
        # O arquivo já voltou ao servidor (a marca `enviado_*` do pacote) e os
        # bytes mudaram depois. Igual pela identidade e sem versão capturada
        # depois da devolução: nada a subir. Qualquer outra coisa para, com o
        # motivo, sem finalizar.
        if identidade is None:
            raise ErroVersionamento(
                'O arquivo de campo {0} mudou depois de devolvido ao servidor e não é mais um repositório '
                'do versionamento legível. Nada foi finalizado.'.format(nome)
            )
        devolvido = versionamento.get('enviado_repo_id')
        if identidade['repo_id'] != devolvido:
            raise ErroVersionamento(
                'O arquivo de campo {0} é do repositório {1}, e o devolvido ao servidor era do {2}. '
                'Nada foi finalizado.'.format(nome, identidade['repo_id'], devolvido)
            )
        novas = identidade['seq'] - int(versionamento['enviado_seq'])
        if novas > 0:
            primeira = int(versionamento['enviado_seq']) + 1
            versoes = 'versão {0}'.format(primeira) if novas == 1 else 'versões {0} a {1}'.format(primeira, identidade['seq'])
            raise ErroVersionamento(
                'O arquivo de campo {0} tem {1} edição(ões) gravada(s) depois de devolvido ao servidor ({2}). '
                'O servidor já tem o arquivo devolvido e não aceita outro, então elas não entrariam na '
                'finalização: nada foi finalizado. Para finalizar com o que o servidor já tem, ponha na pasta '
                'o arquivo como foi devolvido.'.format(nome, novas, versoes)
            )
        if novas < 0:
            raise ErroVersionamento(
                'O arquivo de campo {0} é anterior ao devolvido ao servidor ({1} versões capturadas, e o '
                'devolvido tinha {2}). Nada foi finalizado.'.format(nome, identidade['seq'], versionamento['enviado_seq'])
            )

    @staticmethod
    def _consolidarWal(caminho, nome):
        # O GeoPackage editado pelo QGIS fica em modo WAL: o que não passou pelo
        # checkpoint mora em `<arquivo>-wal`, e só o arquivo principal sobe.
        # Com `-wal` ou `-shm` ao lado, o checkpoint TRUNCATE leva tudo para o
        # arquivo principal; se não der (arquivo aberto em outro programa, ou
        # que não é SQLite), recusa e não sobe nada.
        wal = caminho + '-wal'
        if not ( os.path.exists(wal) or os.path.exists(caminho + '-shm') ):
            return
        recusa = (
            'O arquivo de campo {0} tem edições que ainda não foram gravadas nele (estão em '
            '{0}-wal), e não foi possível consolidá-las{1}. Feche o arquivo no QGIS (e em '
            'qualquer outro programa) e use "Finalizar SAP Local" de novo. Nada foi enviado.'
        )
        try:
            conexao = sqlite3.connect(caminho, timeout=2)
            try:
                ocupado = conexao.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()[0]
            finally:
                conexao.close()
        except sqlite3.Error as e:
            raise Exception(recusa.format(nome, ' ({0})'.format(e)))
        if ocupado or ( os.path.exists(wal) and os.path.getsize(wal) > 0 ):
            raise Exception(recusa.format(nome, ' (o arquivo está em uso)'))

    @staticmethod
    def _sha256(caminho):
        h = hashlib.sha256()
        with open(caminho, 'rb') as f:
            for bloco in iter(lambda: f.read(1024 * 1024), b''):
                h.update(bloco)
        return h.hexdigest()

    # --- Campo da base versionada (contrato, seção 9.2) -----------------------
    #
    # Estas chamadas não passam por `checkError`: as recusas delas (409 com
    # código) são decididas por quem chama, e viram `ErroVersionamento`.

    def _requestSemCaixa(self, method, url, corpo=None, headers=None, **kwargs):
        # `corpo` pode ser uma função que devolve um corpo novo a cada
        # tentativa: o arquivo aberto é consumido pelo envio, e o 401 repete o
        # pedido depois de renovar o login.
        kwargs.setdefault('timeout', TIMEOUT)
        for tentativa in (0, 1):
            cabecalhos = dict(headers or {})
            if self.getToken():
                cabecalhos['authorization'] = self.getToken()
            dados = corpo() if callable(corpo) else corpo
            try:
                response = getattr(self.session, method)(url, data=dados, headers=cabecalhos, **kwargs)
            finally:
                if hasattr(dados, 'close'):
                    dados.close()
            if (
                    response.status_code == 401 and tentativa == 0
                    and not self._isReAuthenticating and self._reAuth()
                ):
                response.close()
                continue
            return response

    @staticmethod
    def _erroDaResposta(response):
        try:
            corpo = response.json()
        except Exception:
            corpo = None
        mensagem = None
        if isinstance(corpo, dict):
            mensagem = corpo.get('message') or corpo.get('error')
        return ErroVersionamento(
            mensagem or 'Erro {0} do servidor.'.format(response.status_code),
            status=response.status_code,
            codigo=codigoDaRecusa(corpo),
            dados=corpo.get('dados') if isinstance(corpo, dict) else None
        )

    def _campoUrl(self, activityId):
        return '{0}/versionamento/atividade/{1}/campo'.format(self.getServer(), int(activityId))

    def downloadFieldFile(self, activityId, folder, repoId=None):
        # `GET /api/versionamento/atividade/:id/campo`, em FLUXO para o disco:
        # o GeoPackage do clone pode ter gigabytes. Grava num `.part` e só o
        # renomeia completo. Devolve o nome do arquivo (sem caminho) e o SHA-256.
        response = self._requestSemCaixa('get', self._campoUrl(activityId), stream=True)
        try:
            if not response.ok:
                raise self._erroDaResposta(response)
            nome = nomeArquivoCampo(response.headers.get('Content-Disposition'), repoId)
            destino = os.path.join(folder, nome)
            if os.path.exists(destino):
                # Pode ser o campo de uma configuração anterior, com edições:
                # nunca sobrescrito.
                raise Exception(
                    'Já existe o arquivo {0} na pasta escolhida. Mova-o antes de configurar de novo.'.format(nome)
                )
            parcial = destino + '.part'
            h = hashlib.sha256()
            try:
                with open(parcial, 'wb') as f:
                    for bloco in response.iter_content(chunk_size=1024 * 1024):
                        if bloco:
                            f.write(bloco)
                            h.update(bloco)
                os.replace(parcial, destino)
            except Exception:
                if os.path.exists(parcial):
                    os.remove(parcial)
                raise
            return nome, h.hexdigest()
        finally:
            response.close()

    def uploadFieldFile(self, activityId, path):
        # `POST /api/versionamento/atividade/:id/campo`, corpo binário em FLUXO
        # (o `requests` lê o arquivo aberto aos pedaços). Com sucesso o servidor
        # limpa o `em_campo` e devolve o que o serviço respondeu.
        tamanho = os.path.getsize(path)
        response = self._requestSemCaixa(
            'post',
            self._campoUrl(activityId),
            corpo=lambda: open(path, 'rb'),
            headers={
                'content-type': 'application/geopackage+sqlite3',
                'content-length': str(tamanho)
            }
        )
        if not response.ok:
            raise self._erroDaResposta(response)
        return response.json()

    def finishLocalModeVersioned(self, corpo):
        # `PUT /api/gerencia_producao/finalizar_modo_local` do tipo 4: 409
        # `campo_pendente` enquanto o campo não voltou, e o 409
        # `conflito_versionamento` (`sessao_id`, `repo_id`, `conflitos`).
        response = self._requestSemCaixa(
            'put',
            "{0}/gerencia_producao/finalizar_modo_local".format(self.getServer()),
            corpo=json.dumps(corpo),
            headers={'content-type': 'application/json'}
        )
        if not response.ok:
            raise self._erroDaResposta(response)
        return response.json()['message']

    def createChangeReport(self, data):
        return self._apiCreate('gerencia_producao/relatorio_alteracao', 'relatorio_alteracao', data)

    def deleteChangeReport(self, data):
        return self._apiDelete('gerencia_producao/relatorio_alteracao', 'relatorio_alteracao_ids', data)

    def getChangeReport(self):
        return self._apiGet('gerencia_producao/relatorio_alteracao')

    def updateChangeReport(self, data):
        return self._apiUpdate('gerencia_producao/relatorio_alteracao', 'relatorio_alteracao', data)

    def resetPropertiesUT(self, data):
        return self._apiUpdate('gerencia_producao/unidade_trabalho/propriedades', 'unidades_trabalho', data)

    def getRemotePluginsPath(self):
        response = self.httpGet(
            url="{0}/gerencia_producao/plugin_path".format(self.getServer())
        )
        if response:
            return response.json()
        return {}

    def updateRemotePluginsPath(self, pluginPath):
        return self._apiUpdate('gerencia_producao/plugin_path', 'plugin_path', pluginPath)

    def createProductLine(self, data):
        response = self.httpPostJson(
            url="{0}/producao/linha_producao".format(self.getServer()),
            postData=data,
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def getProfileDifficultyType(self):
        return self._apiGet('producao/tipo_perfil_dificuldade')

    def createProfileDifficulty(self, data):
        return self._apiCreate('producao/configuracao/perfil_dificuldade_operador', 'perfis_dificuldade_operador', data)

    def deleteProfileDifficulty(self, data):
        return self._apiDelete('producao/configuracao/perfil_dificuldade_operador', 'perfis_dificuldade_operador_ids', data)

    def getProfileDifficulty(self):
        return self._apiGet('producao/configuracao/perfil_dificuldade_operador')

    def updateProfileDifficulty(self, data):
        return self._apiUpdate('producao/configuracao/perfil_dificuldade_operador', 'perfis_dificuldade_operador', data)

    def copySetupLot(self, data):
        response = self.httpPostJson(
            url="{0}/producao/configuracao/lote/copiar".format(self.getServer()),
            postData=data
        )
        if response:
            return response.json()['message']
        return None

    def createWorkflows(self, data):
        return self._apiCreate('producao/workflow', 'workflows', data)

    def deleteWorkflows(self, data):
        return self._apiDelete('producao/workflow', 'workflows_ids', data)

    def getWorkflows(self):
        return self._apiGet('producao/workflow')

    def updateWorkflows(self, data):
        return self._apiUpdate('producao/workflow', 'workflows', data)

    def createWorkflowProfiles(self, data):
        return self._apiCreate('producao/configuracao/perfil_workflow_dsgtools', 'perfil_workflow_dsgtools', data)

    def deleteWorkflowProfiles(self, data):
        return self._apiDelete('producao/configuracao/perfil_workflow_dsgtools', 'perfil_workflow_dsgtools_ids', data)

    def getWorkflowProfiles(self):
        return self._apiGet('producao/configuracao/perfil_workflow_dsgtools')

    def updateWorkflowProfiles(self, data):
        return self._apiUpdate('producao/configuracao/perfil_workflow_dsgtools', 'perfil_workflow_dsgtools', data)

    def createMonitoringProfiles(self, data):
        return self._apiCreate('microcontrole/configuracao/perfil_monitoramento', 'perfis_monitoramento', data)

    def deleteMonitoringProfiles(self, data):
        return self._apiDelete('microcontrole/configuracao/perfil_monitoramento', 'perfis_monitoramento_ids', data)

    def getMonitoringProfiles(self):
        return self._apiGet('microcontrole/configuracao/perfil_monitoramento')

    def updateMonitoringProfiles(self, data):
        return self._apiUpdate('microcontrole/configuracao/perfil_monitoramento', 'perfis_monitoramento', data)

    def getMonitoringTypes(self):
        return self._apiGet('microcontrole/tipo_monitoramento')
    
    def createFilaPrioritaria(self, data):
        # SAP 3.0: o POST é o mesmo de "Definir Atividades Prioritárias".
        return self.setPriorityActivity(
            data['atividade_ids'],
            data['prioridade'],
            data['usuario_uuid']
        )

    def deleteFilaPrioritaria(self, data):
        return self._apiDelete('gerencia_producao/fila_prioritaria', 'fila_prioritaria_ids', data)

    def getFilaPrioritaria(self):
        return self._apiGet('gerencia_producao/fila_prioritaria')

    def updateFilaPrioritaria(self, data):
        return self._apiUpdate('gerencia_producao/fila_prioritaria', 'fila_prioritaria', data)

    def getAtividadeSubfase(self):
        return self._apiGet('acompanhamento/atividade_subfase')
    
    ###############################
    def deleteUTWithoutActivity(self):
        # SAP 3.0: a confirmação é o NOME DA AÇÃO no corpo.
        response = self.httpDeleteJson(
            url="{0}/perigo/ut_sem_atividade".format(self.getServer()),
            postData={
                'confirmar': 'apagar_ut_sem_atividade'
            }
        )
        if response:
            return response.json()['message']
        return []

    def getResumoUsuario(self):
        response = self.httpGet(
            url="{0}/acompanhamento/resumo_usuario".format(self.getServer())
        )
        if response:
            return response.json().get('dados', [])
        return []
    
    def getAlteracaoFluxo(self):
        response = self.httpGet(
            url="{0}/gerencia_producao/alteracao_fluxo".format(self.getServer())
        )
        if response:
            return response.json().get('dados', [])
        return []

    def atualizaAlteracaoFluxo(self, data):
        return self._apiUpdate('gerencia_producao/alteracao_fluxo', 'alteracao_fluxo', data)

    ## Metadados (alimentam o JSON de edicao da carta)
    def getInformacoesEdicao(self):
        return self._apiGet('metadados/informacoes_edicao')

    def criaInformacoesEdicao(self, data):
        return self._apiCreate('metadados/informacoes_edicao', 'informacoes_edicao', data)

    def atualizaInformacoesEdicao(self, data):
        return self._apiUpdate('metadados/informacoes_edicao', 'informacoes_edicao', data)

    def deletaInformacoesEdicao(self, ids):
        return self._apiDelete('metadados/informacoes_edicao', 'informacoes_edicao_ids', ids)

    def getSensorCartaOrtoimagem(self):
        return self._apiGet('metadados/sensor_carta_ortoimagem')

    def criaSensorCartaOrtoimagem(self, data):
        return self._apiCreate('metadados/sensor_carta_ortoimagem', 'sensor_carta_ortoimagem', data)

    def atualizaSensorCartaOrtoimagem(self, data):
        return self._apiUpdate('metadados/sensor_carta_ortoimagem', 'sensor_carta_ortoimagem', data)

    def deletaSensorCartaOrtoimagem(self, ids):
        return self._apiDelete('metadados/sensor_carta_ortoimagem', 'sensor_carta_ortoimagem_ids', ids)

    def getImagensCartaOrtoimagem(self):
        return self._apiGet('metadados/imagens_carta_ortoimagem')

    def criaImagensCartaOrtoimagem(self, data):
        return self._apiCreate('metadados/imagens_carta_ortoimagem', 'imagens_carta_ortoimagem', data)

    def atualizaImagensCartaOrtoimagem(self, data):
        return self._apiUpdate('metadados/imagens_carta_ortoimagem', 'imagens_carta_ortoimagem', data)

    def deletaImagensCartaOrtoimagem(self, ids):
        return self._apiDelete('metadados/imagens_carta_ortoimagem', 'imagens_carta_ortoimagem_ids', ids)

    def getClassesComplementaresOrto(self):
        return self._apiGet('metadados/classes_complementares_orto')

    def criaClassesComplementaresOrto(self, data):
        return self._apiCreate('metadados/classes_complementares_orto', 'classes_complementares_orto', data)

    def atualizaClassesComplementaresOrto(self, data):
        return self._apiUpdate('metadados/classes_complementares_orto', 'classes_complementares_orto', data)

    def deletaClassesComplementaresOrto(self, ids):
        return self._apiDelete('metadados/classes_complementares_orto', 'classes_complementares_orto_ids', ids)

    def getPerfilClassesComplementaresOrto(self):
        return self._apiGet('metadados/perfil_classes_complementares_orto')

    def criaPerfilClassesComplementaresOrto(self, data):
        return self._apiCreate('metadados/perfil_classes_complementares_orto', 'perfil_classes_complementares_orto', data)

    def atualizaPerfilClassesComplementaresOrto(self, data):
        return self._apiUpdate('metadados/perfil_classes_complementares_orto', 'perfil_classes_complementares_orto', data)

    def deletaPerfilClassesComplementaresOrto(self, ids):
        return self._apiDelete('metadados/perfil_classes_complementares_orto', 'perfil_classes_complementares_orto_ids', ids)

    def getCreditosQpt(self):
        return self._apiGet('metadados/creditos_qpt')

    def criaCreditosQpt(self, data):
        return self._apiCreate('metadados/creditos_qpt', 'creditos_qpt', data)

    def atualizaCreditosQpt(self, data):
        return self._apiUpdate('metadados/creditos_qpt', 'creditos_qpt', data)

    def deletaCreditosQpt(self, ids):
        return self._apiDelete('metadados/creditos_qpt', 'creditos_qpt_ids', ids)

    def getResponsavelFaseProduto(self):
        return self._apiGet('metadados/responsavel_fase_produto')

    def criaResponsavelFaseProduto(self, data):
        return self._apiCreate('metadados/responsavel_fase_produto', 'responsavel_fase_produto', data)

    def deletaResponsavelFaseProduto(self, ids):
        return self._apiDelete('metadados/responsavel_fase_produto', 'responsavel_fase_produto_ids', ids)

    ## JSON de edicao gerado pelo backend (uma folha por produto do lote)
    def getJsonEdicaoLote(self, loteId):
        response = self.httpGet(
            url="{0}/metadados/json_edicao/lote/{1}".format(self.getServer(), loteId)
        )
        if response:
            return response.json()['dados']
        return []

    def getProdutosDoLote(self, loteId):
        # O alvo do metadado no SAP 3.0 é a VERSÃO (`versao_id`): cada linha traz
        # o `id` da versão e o `inom`, `mi` e `nome` da folha, sem Registro Histórico.
        return self._apiGet('gerencia_producao/lote/{0}/versoes'.format(loteId))

    def getMetadadoXmlLote(self, loteId):
        response = self.httpGet(
            url="{0}/metadados/xml/lote/{1}".format(self.getServer(), loteId)
        )
        if response:
            return response.json()['dados']
        return []

    def getInformacoesProduto(self):
        return self._apiGet('metadados/informacoes_produto')

    def criaInformacoesProduto(self, data):
        return self._apiCreate('metadados/informacoes_produto', 'informacoes_produto', data)

    def atualizaInformacoesProduto(self, data):
        return self._apiUpdate('metadados/informacoes_produto', 'informacoes_produto', data)

    def deletaInformacoesProduto(self, ids):
        return self._apiDelete('metadados/informacoes_produto', 'informacoes_produto_ids', ids)

    def getPalavraChaveProduto(self):
        return self._apiGet('metadados/palavra_chave_produto')

    def criaPalavraChaveProduto(self, data):
        return self._apiCreate('metadados/palavra_chave_produto', 'palavras_chave_produto', data)

    def deletaPalavraChaveProduto(self, ids):
        return self._apiDelete('metadados/palavra_chave_produto', 'palavras_chave_produto_ids', ids)

    def getMetadadoUsuarios(self):
        return self._apiGet('metadados/usuario')

    def criaMetadadoUsuarios(self, data):
        return self._apiCreate('metadados/usuario', 'usuario', data)

    def atualizaMetadadoUsuarios(self, data):
        return self._apiUpdate('metadados/usuario', 'usuario', data)

    def deletaMetadadoUsuarios(self, ids):
        return self._apiDelete('metadados/usuario', 'usuarios_ids', ids)

    # dominios de metadado (para preencher os combos)
    def getMetadadoOrganizacao(self):
        return self._apiGet('metadados/organizacao')

    def atualizaMetadadoOrganizacao(self, data):
        return self._apiUpdate('metadados/organizacao', 'organizacoes', data)

    def getMetadadoEspecificacao(self):
        return self._apiGet('metadados/especificacao')

    def getMetadadoDatumVertical(self):
        return self._apiGet('metadados/datum_vertical')

    def getMetadadoCodigoRestricao(self):
        return self._apiGet('metadados/codigo_restricao')

    def getMetadadoCodigoClassificacao(self):
        return self._apiGet('metadados/codigo_classificacao')

    def getMetadadoTipoPalavraChave(self):
        return self._apiGet('metadados/tipo_palavra_chave')

    # --- Versionamento (contrato do versionamento no SAP 3.0, seção 5) ---------
    #
    # O QGIS fala só com o SAP. O ciclo (lote, bloco, descarte) é rota do SAP; o
    # que é do serviço passa pelo repasse `/api/versionamento/servico/*`, que
    # devolve a resposta do serviço como veio (sem o envelope do SAP).

    def versionarLote(self, loteId, dadoProducaoId):
        # 202 com `job_id`: o clone da base para o lote é tarefa longa.
        return self._apiPostEnvelope(
            'versionamento/lote/{0}'.format(int(loteId)),
            {'dado_producao_id': int(dadoProducaoId)}
        )

    def versionarBloco(self, blocoId):
        return self._apiPostEnvelope(
            'versionamento/bloco/{0}'.format(int(blocoId)),
            {}
        )

    def criarIntegracaoLote(self, loteId, subfaseId, dadoProducaoId=None):
        # `POST /api/versionamento/lote/:lote_id/integracao` (contrato 9.2): a
        # atividade de integração do lote na base, numa UT com a geometria do
        # lote. `dado_producao_id` só vai quando escolhido (o servidor o pede
        # quando o lote tem mais de uma base versionada).
        corpo = {'subfase_id': int(subfaseId)}
        if dadoProducaoId:
            corpo['dado_producao_id'] = int(dadoProducaoId)
        return self._apiPostEnvelope(
            'versionamento/lote/{0}/integracao'.format(int(loteId)),
            corpo
        )

    def criarIntegracaoBloco(self, blocoId, subfaseId, dadoProducaoId=None):
        # `POST /api/versionamento/bloco/:bloco_id/integracao` (contrato,
        # seção 5): a atividade de integração do bloco no lote, numa UT com a
        # geometria do bloco. `dado_producao_id` só vai quando escolhido.
        corpo = {'subfase_id': int(subfaseId)}
        if dadoProducaoId:
            corpo['dado_producao_id'] = int(dadoProducaoId)
        return self._apiPostEnvelope(
            'versionamento/bloco/{0}/integracao'.format(int(blocoId)),
            corpo
        )

    def getRepositoriosVersionamento(self, loteId=None, blocoId=None):
        params = []
        if loteId:
            params.append('lote_id={0}'.format(int(loteId)))
        if blocoId:
            params.append('bloco_id={0}'.format(int(blocoId)))
        query = '?' + '&'.join(params) if params else ''
        return self._apiGet('versionamento/repositorios{0}'.format(query))

    def descartarRepositorio(self, repositorioId, motivo):
        return self._apiCreate(
            'versionamento/repositorio/{0}/descartar'.format(int(repositorioId)),
            'motivo',
            motivo
        )

    def _servicoUrl(self, caminho):
        return '{0}/versionamento/servico/{1}'.format(self.getServer(), caminho)

    @staticmethod
    def _corpoDoServico(corpo):
        # O repasse devolve o corpo do serviço; se vier no envelope do SAP, a
        # carga está em `dados`.
        if isinstance(corpo, dict) and 'dados' in corpo and 'success' in corpo:
            return corpo['dados']
        return corpo

    def versionamentoServicoGet(self, caminho, timeout=30):
        # SEM caixa de mensagem: serve à tarefa em segundo plano (QgsTask), que
        # não pode tocar a interface, e às leituras opcionais. Erro vira exceção
        # com a mensagem do servidor. Sessão própria: a do plugin é da linha
        # principal.
        sessao = requests.Session()
        sessao.trust_env = False
        sessao.verify = SSL_VERIFY
        try:
            response = sessao.get(
                self._servicoUrl(caminho),
                headers={'authorization': self.getToken() or ''},
                timeout=timeout
            )
        finally:
            sessao.close()
        if not response.ok:
            try:
                corpo = response.json()
                mensagem = corpo.get('message') or corpo.get('error') or ''
            except Exception:
                mensagem = ''
            raise Exception(mensagem or 'Erro {0} do servidor.'.format(response.status_code))
        return self._corpoDoServico(response.json())

    def getVersionamentoRepos(self):
        # A lista das bases no serviço, para escolher o `repo_id` do dado de
        # produção tipo 4. O repasse pode não liberar `GET /repos` ao gerente
        # (403): aí a lista vem vazia e o `repo_id` é digitado.
        try:
            corpo = self.versionamentoServicoGet('repos?details=false', timeout=15)
        except Exception:
            return []
        repos = corpo.get('repositories') if isinstance(corpo, dict) else corpo
        return [r for r in (repos or []) if isinstance(r, dict) and r.get('id')]

    def getVersionamentoDatasets(self, repoId):
        response = self.httpGet(
            url=self._servicoUrl('repos/{0}/datasets'.format(requests.utils.quote(str(repoId), safe='')))
        )
        if not response:
            return []
        corpo = self._corpoDoServico(response.json())
        datasets = corpo.get('datasets') if isinstance(corpo, dict) else corpo
        return [
            d['name'] if isinstance(d, dict) else d
            for d in (datasets or [])
            if (isinstance(d, dict) and d.get('name')) or isinstance(d, str)
        ]

    def getVersionamentoJob(self, jobId):
        return self.versionamentoServicoGet(
            'jobs/{0}'.format(requests.utils.quote(str(jobId), safe=''))
        )
