import json, requests, socket
import os
import re
import psycopg2
from SAP_Gerente.modules.sap.factories.loginSingleton import LoginSingleton
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory
from SAP_Gerente.modules.sap.factories.dataModelFactory import DataModelFactory
from SAP_Gerente.modules.sap.postgresql import Postgresql

SSL_VERIFY=False

TIMEOUT = 60 * 2

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

    def downloadQgisProject(self, destPath):
        try:
            projectXml = self.getQgisProject()
            with open(destPath, 'w') as f:
                f.write(projectXml)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', 'Projeto criado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

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
        if response.status_code == 403 and not self._isReAuthenticating and self._reAuth():
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
            url="{0}/gerencia/perfil_producao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return [{'nome': 'Sem perfis de produção', 'id': False}]
    
    def createProductionProfiles(self, data):
        return self._apiCreate('gerencia/perfil_producao', 'perfil_producao', data)

    def updateProductionProfiles(self, data):
        return self._apiUpdate('gerencia/perfil_producao', 'perfil_producao', data)

    def deleteProductionProfiles(self, data):
        return self._apiDelete('gerencia/perfil_producao', 'perfil_producao_ids', data)

    def getActiveUsers(self):
        response = self.httpGet(
            url="{0}/usuarios".format(self.getServer())
        )
        if response:
            activeUses = list(filter(lambda item: item['ativo'], response.json()['dados']))
            activeUses.sort(key=lambda item: item['nome'])
            return activeUses
        return [{'nome': 'Sem usuários', 'id': False}]

    def getUsers(self):
        response = self.httpGet(
            url="{0}/usuarios".format(self.getServer())
        )
        if response:
            users = response.json()['dados']
            users.sort(key=lambda item: item['nome'])
            return users
        return [{'nome': 'Sem usuários', 'id': False}]

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
            raise Exception("Versão do servidor sap errada")
        if not self.isAdminUser(responseJson):
            raise Exception("Usuário não é administrador")
        return responseJson

    def validVersion(self, responseJson):
        return ('version' in responseJson and responseJson['version'].split('.')[0] == '2')

    def isAdminUser(self, responseJson):
        return ('administrador' in responseJson['dados'] and responseJson['dados']['administrador'])

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
        if response.status_code == 403:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', 'Token expirado, faça o login novamente!')
            return False
        if not response.ok:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', response.json()['message'])
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
            url="{0}/gerencia/atividade/avancar".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "concluida" : endStep
            }
        )
        if response:
            return response.json()['message']
        return None

    def createPriorityGroupActivity(self, activityIds, priority, profileId):
        fila = []
        for a in activityIds:
            aux = {
                "atividade_id" : a,
                "prioridade" : int(priority),
                "perfil_producao_id" : profileId
            }
            fila.append(aux)

        response = self.httpPostJson(
            url="{0}/gerencia/fila_prioritaria_grupo".format(self.getServer()),
            postData={
                "fila_prioritaria_grupo": fila
            }
        )
        if response:
            return response.json()['message']
        return None

    def fillCommentActivity(self, activityIds, commentActivity, commentWorkspace):
        response = self.httpPutJson(
            url="{0}/gerencia/observacao".format(self.getServer()),
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
            url="{0}/gerencia/atividade/{1}/observacao".format(self.getServer(), activityId)
        )
        return response.json()['dados']

    def openActivity(self, activityId):
        response = self.httpGet(
            url="{0}/gerencia/atividade/{1}".format(self.getServer(), activityId),
        )
        if response:
            return response.json()
        return None

    #interface
    def openNextActivityByUser(self, userId, nextActivity):
        params = '?proxima=true' if nextActivity else ''
        response = self.httpGet(
            url="{0}/gerencia/atividade/usuario/{1}{2}".format(self.getServer(), userId, params)
        )
        if response:
            return response.json()
        return None
        
    #interface
    def lockWorkspace(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/unidade_trabalho/disponivel".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : False
            }
        )
        if response:
            return response.json()['message']
        return None

    #interface
    def pauseActivity(self, workspacesIds):
        return self._apiCreate('gerencia/atividade/pausar', 'unidade_trabalho_ids', workspacesIds)

    #interface
    def restartActivity(self, workspacesIds):
        return self._apiCreate('gerencia/atividade/reiniciar', 'unidade_trabalho_ids', workspacesIds)
    
    #interface
    def returnActivityToPreviousStep(self, activityIds, preserveUser):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/voltar".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "manter_usuarios" : preserveUser
            }
        )
        if response:
            return response.json()['message']
        return None

    #interface
    def setPriorityActivity(self, activityIds, priority, userId):
        fila = {
            "atividade_ids" : activityIds,
            "prioridade" : int(priority),
            "usuario_prioridade_id" : userId
        }

        response = self.httpPostJson(
            url="{0}/gerencia/fila_prioritaria".format(self.getServer()),
            postData=fila
        )
        if response:
            return response.json()['message']
        return None

     #interface
    def unlockWorkspace(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/unidade_trabalho/disponivel".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : True
            }
        )
        if response:
            return response.json()['message']
        return None

    def getStyles(self):
        return self._apiGet('projeto/estilos')

    def getGroupStyles(self):
        return self._apiGet('projeto/grupo_estilos')

    def createGroupStyles(self, data):
        return self._apiCreate('projeto/grupo_estilos', 'grupo_estilos', data)

    def deleteGroupStyles(self, data):
        return self._apiDelete('projeto/grupo_estilos', 'grupo_estilos_ids', data)

    def updateGroupStyles(self, data):
        return self._apiUpdate('projeto/grupo_estilos', 'grupo_estilos', data)

    def getStyleNames(self):
        return self._apiGet('projeto/estilos')

    def createStyles(self, data):
        return self._apiCreate('projeto/estilos', 'estilos', data)

    def updateStyles(self, data):
        return self._apiUpdate('projeto/estilos', 'estilos', data)

    def deleteStyles(self, ids):
        return self._apiDelete('projeto/estilos', 'estilos_ids', ids)

    def getModels(self):
        return self._apiGet('projeto/modelos')

    def createModels(self, data):
        return self._apiCreate('projeto/modelos', 'modelos', data)

    def updateModels(self, data):
        return self._apiUpdate('projeto/modelos', 'modelos', data)

    def deleteModels(self, ids):
        return self._apiDelete('projeto/modelos', 'modelos_ids', ids)

    def getRules(self):
        return self._apiGet('projeto/regras')

    def createRules(self, data):
        return self._apiCreate('projeto/regras', 'regras', data)

    def updateRules(self, data):
        return self._apiUpdate('projeto/regras', 'regras', data)

    def deleteRules(self, ids):
        return self._apiDelete('projeto/regras', 'regras_ids', ids)

    def getRuleSet(self):
        return self._apiGet('projeto/grupo_regras')

    def createRuleSet(self, data):
        return self._apiCreate('projeto/grupo_regras', 'grupo_regras', data)

    def updateRuleSet(self, data):
        return self._apiUpdate('projeto/grupo_regras', 'grupo_regras', data)

    def deleteRuleSet(self, ids):
        return self._apiDelete('projeto/grupo_regras', 'grupo_regras_ids', ids)
    
    def getQgisProject(self):
        response = self.httpGet(
            url="{0}/gerencia/projeto_qgis".format(self.getServer())
        )
        if response:
            return response.json()['dados']['projeto']
        return []

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
            url="{0}/gerencia/view_acompanhamento{1}".format(self.getServer(), query_string)
        )
        
        if response:
            return response.json()['dados']
        return []

    def updateBlockedActivities(self):
        response = self.httpPut(
            url="{0}/gerencia/atividades_bloqueadas".format(self.getServer())
        )
        if response:
            return response.json()['message']
        return None

    def synchronizeUserInformation(self):
        response = self.httpPut(
            url="{0}/usuarios/sincronizar".format(self.getServer())
        )
        if response:
            return response.json()['message']
        return None

    def getUsersFromAuthService(self):
        return self._apiGet('usuarios/servico_autenticacao')

    def importUsersAuthService(self, usersIds):
        return self._apiCreate('usuarios', 'usuarios', usersIds)

    def updateUsersPrivileges(self, usersData):
        return self._apiUpdate('usuarios', 'usuarios', usersData)

    def deleteActivities(self, activityIds):
        return self._apiDelete('projeto/atividades', 'atividades_ids', activityIds)
    
    def createActivities(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/atividades".format(self.getServer()),
            postData=data    
        )
        if response:
            return response.json()['message']
        return None

    def getDatabases(self):
        return self._apiGet('projeto/banco_dados')

    def getAuthDatabase(self):
        return self._apiGet('projeto/login')

    def resetPrivileges(self):
        response = self.httpPut(
            url="{0}/gerencia/atividades/permissoes".format(self.getServer()),
            timeout=60*5
        )
        if response:
            return response.json()['message']
        return None

    def importLayers(self, layersImported):
        return self._apiCreate('projeto/configuracao/camadas', 'camadas', layersImported)

    def getLayers(self):
        return self._apiGet('projeto/configuracao/camadas')

    def deleteLayers(self, layersIds):
        return self._apiDelete('projeto/configuracao/camadas', 'camadas_ids', layersIds)

    def updateLayers(self, layersData):
        return self._apiUpdate('projeto/configuracao/camadas', 'camadas', layersData)

    def getLots(self):
        return self._apiGet('projeto/lote?status=execucao')

    def getAllLots(self):
        return self._apiGet('projeto/lote')

    def alterBlock(self, workspacesIds, lotId):
        response = self.httpPutJson(
            url="{0}/projeto/unidade_trabalho/bloco".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'bloco_id': lotId
            }    
        )
        if response:
            return response.json()['message']
        return None

    def revokePrivileges(self, dbHost, dbPort, dbName):
        response = self.httpPostJson(
            url="{0}/gerencia/banco_dados/revogar_permissoes".format(self.getServer()),
            postData={
                "servidor" : dbHost,
                "porta" : int(dbPort),
                "banco" : dbName
            }
        )
        if response:
            return response.json()['message']
        return None

    def getFmeServers(self):
        return self._apiGet('projeto/configuracao/gerenciador_fme')

    def createFmeServers(self, fmeServers):
        return self._apiCreate('projeto/configuracao/gerenciador_fme', 'gerenciador_fme', fmeServers)

    def updateFmeServers(self, fmeServers):
        return self._apiUpdate('projeto/configuracao/gerenciador_fme', 'gerenciador_fme', fmeServers)

    def deleteFmeServers(self, fmeServersIds):
        return self._apiDelete('projeto/configuracao/gerenciador_fme', 'servidores_id', fmeServersIds)

    def getFmeProfiles(self):
        return self._apiGet('projeto/configuracao/perfil_fme')

    def createFmeProfiles(self, fmeProfiles):
        return self._apiCreate('projeto/configuracao/perfil_fme', 'perfis_fme', fmeProfiles)

    def updateFmeProfiles(self, fmeProfiles):
        return self._apiUpdate('projeto/configuracao/perfil_fme', 'perfis_fme', fmeProfiles)

    def deleteFmeProfiles(self, fmeProfilesIds):
        return self._apiDelete('projeto/configuracao/perfil_fme', 'perfil_fme_ids', fmeProfilesIds)
    
    def getPhases(self):
        return self._apiGet('projeto/fases')

    def getSubphases(self):
        return self._apiGet('projeto/subfases')

    def getActiveSubphases(self):
        return self._apiGet('projeto/subfases?status=ativo')

    def getSteps(self):
        return self._apiGet('projeto/etapas')

    def deleteUserActivities(self, userId):
        response = self.httpDelete(
            url="{0}/perigo/atividades/usuario/{1}".format(self.getServer(), userId)
        )
        if response:
            return response.json()['message']
        return []

    def getInputTypes(self):
        return self._apiGet('projeto/tipo_insumo')

    def getAllInputGroups(self):
        return self._apiGet('projeto/grupo_insumo')

    def getInputGroups(self):
        return self._apiGet('projeto/grupo_insumo?disponivel=true')

    def createInputGroups(self, inputGroups):
        return self._apiCreate('projeto/grupo_insumo', 'grupo_insumos', inputGroups)

    def updateInputGroups(self, inputGroups):
        return self._apiUpdate('projeto/grupo_insumo', 'grupo_insumos', inputGroups)

    def deleteInputGroups(self, inputGroupIds):
        return self._apiDelete('projeto/grupo_insumo', 'grupo_insumos_ids', inputGroupIds)

    def deleteAssociatedInputs(self, workspacesIds, inputGroupId):
        response = self.httpDeleteJson(
            url="{0}/projeto/unidade_trabalho/insumos".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'grupo_insumo_id': inputGroupId
            }  
        )
        if response:
            return response.json()['message']
        return None

    def deleteWorkUnits(self, workspacesIds):
        return self._apiDelete('projeto/unidade_trabalho', 'unidade_trabalho_ids', workspacesIds)

    def getProductionLines(self):
        def sortByName(elem):
            return elem['linha_producao']
        response = self.httpGet(
            url="{0}/projeto/linha_producao".format(self.getServer())
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
            url="{0}/projeto/linha_producao?status=ativo".format(self.getServer())
        )
        if response:
            productionLines = response.json()['dados']
            productionLines.sort(key=sortByName)
            return productionLines
        return []

    def createInputs(self, inputGroupCode, inputGroupId, inputs):
        response = self.httpPostJson(
            url="{0}/projeto/insumo".format(self.getServer()),
            postData={
                'tipo_insumo': inputGroupCode,
                'grupo_insumo': inputGroupId,
                'insumos': inputs
            }   
        )
        if response:
            return response.json()['message']
        return None

    def createProducts(self, lotId, products):
        response = self.httpPostJson(
            url="{0}/projeto/produto".format(self.getServer()),
            postData={
                'lote_id': lotId,
                'produtos': products
            }   
        )
        if response:
            return response.json()['message']
        return None

    def getRoutines(self):
        return self._apiGet('projeto/tipo_rotina')

    def getAssociationStrategies(self):
        return self._apiGet('projeto/tipo_estrategia_associacao')

    def associateInputs(self, workspacesIds, inputGroupId, associationStrategyId, defaultPath):
        response = self.httpPostJson(
            url="{0}/projeto/unidade_trabalho/insumos".format(self.getServer()),
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
            url="{0}/projeto/unidade_trabalho".format(self.getServer()),
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
        return self._apiGet('projeto/dado_producao')

    def getProductionDataType(self):
        return self._apiGet('projeto/tipo_dado_producao')

    def copyWorkUnit(self, workspacesIds, stepsIds, associateInputs):
        response = self.httpPostJson(
            url="{0}/projeto/unidade_trabalho/copiar".format(self.getServer()),
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
        return self._apiGet('projeto/configuracao/perfil_modelo')

    def createModelProfiles(self, data):
        return self._apiCreate('projeto/configuracao/perfil_modelo', 'perfis_modelo', data)

    def updateModelProfiles(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_modelo', 'perfis_modelo', data)

    def deleteModelProfiles(self, ids):
        return self._apiDelete('projeto/configuracao/perfil_modelo', 'perfil_modelo_ids', ids)

    def getRuleProfiles(self):
        return self._apiGet('projeto/configuracao/perfil_regras')

    def createRuleProfiles(self, data):
        return self._apiCreate('projeto/configuracao/perfil_regras', 'perfis_regras', data)

    def updateLinhaProducao(self, data):
        return self._apiUpdate('projeto/linha_producao', 'linhas_producao', data)

    def updateRuleProfiles(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_regras', 'perfis_regras', data)

    def deleteRuleProfiles(self, ids):
        return self._apiDelete('projeto/configuracao/perfil_regras', 'perfil_regras_ids', ids)

    def getStyleProfiles(self):
        return self._apiGet('projeto/configuracao/perfil_estilos')

    def createStyleProfiles(self, data):
        return self._apiCreate('projeto/configuracao/perfil_estilos', 'perfis_estilos', data)

    def updateStyleProfiles(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_estilos', 'perfis_estilos', data)

    def deleteStyleProfiles(self, ids):
        return self._apiDelete('projeto/configuracao/perfil_estilos', 'perfil_estilos_ids', ids)

    def getProjects(self):
        return self._apiGet('projeto/projetos?status=execucao')

    def getAllProjects(self):
        return self._apiGet('projeto/projetos')

    def getStepType(self):
        return self._apiGet('projeto/tipo_etapa')

    def getProfileProductionStep(self):
        return self._apiGet('gerencia/perfil_producao_etapa')

    def createProfileProductionStep(self, data):
        return self._apiCreate('gerencia/perfil_producao_etapa', 'perfil_producao_etapa', data)

    def updateProfileProductionStep(self, data):
        return self._apiUpdate('gerencia/perfil_producao_etapa', 'perfil_producao_etapa', data)

    def deleteProfileProductionStep(self, data):
        return self._apiDelete('gerencia/perfil_producao_etapa', 'perfil_producao_etapa_ids', data)

    def getUserProfileProduction(self):
        return self._apiGet('gerencia/perfil_producao_operador')

    def createUserProfileProduction(self, data):
        return self._apiCreate('gerencia/perfil_producao_operador', 'perfil_producao_operador', data)

    def updateUserProfileProduction(self, data):
        return self._apiUpdate('gerencia/perfil_producao_operador', 'perfil_producao_operador', data)

    def deleteUserProfileProduction(self, data):
        return self._apiDelete('gerencia/perfil_producao_operador', 'perfil_producao_operador_ids', data)

    def getUserBlocks(self):
        return self._apiGet('gerencia/perfil_bloco_operador')

    def createUserBlockProduction(self, data):
        return self._apiCreate('gerencia/perfil_bloco_operador', 'perfil_bloco_operador', data)

    def updateUserBlockProduction(self, data):
        return self._apiUpdate('gerencia/perfil_bloco_operador', 'perfil_bloco_operador', data)

    def deleteUserBlockProduction(self, data):
        return self._apiDelete('gerencia/perfil_bloco_operador', 'perfil_bloco_operador_ids', data)

    def getBlocks(self):
        return self._apiGet('projeto/bloco?status=execucao')

    def getAllBlocks(self):
        return self._apiGet('projeto/bloco')

    def createMenus(self, data):
        return self._apiCreate('projeto/menus', 'menus', data)

    def updateMenus(self, data):
        return self._apiUpdate('projeto/menus', 'menus', data)

    def deleteMenus(self, data):
        return self._apiDelete('projeto/menus', 'menus_ids', data)

    def getMenus(self):
        return self._apiGet('projeto/menus')

    def getMenuProfiles(self):
        return self._apiGet('projeto/configuracao/perfil_menu')

    def createMenuProfiles(self, data):
        return self._apiCreate('projeto/configuracao/perfil_menu', 'perfis_menu', data)

    def updateMenuProfiles(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_menu', 'perfis_menu', data)

    def deleteMenuProfiles(self, data):
        return self._apiDelete('projeto/configuracao/perfil_menu', 'perfil_menu_ids', data)

    def createAllActivities(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/atividades/todas".format(self.getServer()),
            postData=data,
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def createDefaultStep(self, padraoCq, phaseId, lotId):
        response = self.httpPostJson(
            url="{0}/projeto/etapas/padrao".format(self.getServer()),
            postData={
                'padrao_cq': padraoCq,
                'fase_id': phaseId,
                'lote_id': lotId,
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def deleteWorkUnitActivities(self, workUnitIds):
        return self._apiDelete('projeto/unidade_trabalho/atividades', 'unidade_trabalho_ids', workUnitIds)

    def updateLayersQgisProject(self):
        response = self.httpPut(
            url="{0}/gerencia/refresh_views".format(self.getServer())
        )
        if response:
            return response.json()['message']
        return None

    def createProjects(self, data):
        return self._apiCreate('projeto/projetos', 'projetos', data)

    def deleteProjects(self, data):
        return self._apiDelete('projeto/projetos', 'projeto_ids', data)

    def updateProjects(self, data):
        return self._apiUpdate('projeto/projetos', 'projetos', data)

    def createLots(self, data):
        return self._apiCreate('projeto/lote', 'lotes', data)

    def deleteLots(self, data):
        return self._apiDelete('projeto/lote', 'lote_ids', data)

    def updateLots(self, data):
        return self._apiUpdate('projeto/lote', 'lotes', data)

    def createBlocks(self, data):
        return self._apiCreate('projeto/bloco', 'blocos', data)

    def deleteBlocks(self, data):
        return self._apiDelete('projeto/bloco', 'bloco_ids', data)

    def updateBlocks(self, data):
        return self._apiUpdate('projeto/bloco', 'blocos', data)

    def createProductionData(self, data):
        return self._apiCreate('projeto/dado_producao', 'dado_producao', data)

    def deleteProductionData(self, data):
        return self._apiDelete('projeto/dado_producao', 'dado_producao_ids', data)

    def updateProductionData(self, data):
        return self._apiUpdate('projeto/dado_producao', 'dado_producao', data)

    def createBlockInputs(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/bloco/insumos".format(self.getServer()),
            postData=data
        )
        if response:
            return response.json()['message']
        return None

    def revokeUserPrivileges(self, data):
        response = self.httpPostJson(
            url="{0}/gerencia/banco_dados/revogar_permissoes_usuario".format(self.getServer()),
            postData=data
        )
        if response:
            return response.json()['message']
        return None

    def getQgisVersion(self):
        return self._apiGet('gerencia/versao_qgis')

    def updateQgisVersion(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia/versao_qgis".format(self.getServer()),
            postData=data
        )
        if response:
            return response.json()['message']
        return None

    def getProfileFinalization(self):
        return self._apiGet('projeto/configuracao/perfil_requisito_finalizacao')

    def updateProfileFinalization(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_requisito_finalizacao', 'perfis_requisito', data)

    def createProfileFinalization(self, data):
        return self._apiCreate('projeto/configuracao/perfil_requisito_finalizacao', 'perfis_requisito', data)

    def deleteProfileFinalization(self, data):
        return self._apiDelete('projeto/configuracao/perfil_requisito_finalizacao', 'perfil_requisito_ids', data)

    def getAlias(self):
        return self._apiGet('projeto/alias')

    def updateAlias(self, data):
        return self._apiUpdate('projeto/alias', 'alias', data)

    def createAlias(self, data):
        return self._apiCreate('projeto/alias', 'alias', data)

    def deleteAlias(self, data):
        return self._apiDelete('projeto/alias', 'alias_ids', data)

    def getAliasProfile(self):
        return self._apiGet('projeto/configuracao/perfil_alias')

    def updateAliasProfile(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_alias', 'perfis_alias', data)

    def createAliasProfile(self, data):
        return self._apiCreate('projeto/configuracao/perfil_alias', 'perfis_alias', data)

    def deleteAliasProfile(self, data):
        return self._apiDelete('projeto/configuracao/perfil_alias', 'perfis_alias_ids', data)

    def getPlugins(self):
        return self._apiGet('gerencia/plugins')

    def updatePlugins(self, data):
        return self._apiUpdate('gerencia/plugins', 'plugins', data)

    def createPlugins(self, data):
        return self._apiCreate('gerencia/plugins', 'plugins', data)

    def deletePlugins(self, data):
        return self._apiDelete('gerencia/plugins', 'plugins_ids', data)

    def getShortcuts(self):
        return self._apiGet('gerencia/atalhos')

    def updateShortcuts(self, data):
        return self._apiUpdate('gerencia/atalhos', 'qgis_shortcuts', data)

    def createShortcuts(self, data):
        return self._apiCreate('gerencia/atalhos', 'qgis_shortcuts', data)

    def deleteShortcuts(self, data):
        return self._apiDelete('gerencia/atalhos', 'qgis_shortcuts_ids', data)

    def getStatusDomain(self):
        return self._apiGet('projeto/status')

    def getShowTypes(self):
        return self._apiGet('projeto/tipo_exibicao')

    def getLineages(self):
        return self._apiGet('projeto/configuracao/perfil_linhagem')

    def updateLineages(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_linhagem', 'perfis_linhagem', data)

    def createLineages(self, data):
        return self._apiCreate('projeto/configuracao/perfil_linhagem', 'perfis_linhagem', data)

    def deleteLineages(self, data):
        return self._apiDelete('projeto/configuracao/perfil_linhagem', 'perfil_linhagem_ids', data)

    def getProblemActivity(self):
        return self._apiGet('gerencia/problema_atividade')

    def updateProblemActivity(self, data):
        return self._apiUpdate('gerencia/problema_atividade', 'problema_atividade', data)

    def getThemes(self):
        return self._apiGet('projeto/temas')

    def updateThemes(self, data):
        return self._apiUpdate('projeto/temas', 'temas', data)

    def createThemes(self, data):
        return self._apiCreate('projeto/temas', 'temas', data)

    def deleteThemes(self, data):
        return self._apiDelete('projeto/temas', 'temas_ids', data)

    def getThemesProfile(self):
        return self._apiGet('projeto/configuracao/perfil_temas')

    def updateThemesProfile(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_temas', 'perfis_temas', data)

    def createThemesProfile(self, data):
        return self._apiCreate('projeto/configuracao/perfil_temas', 'perfis_temas', data)

    def deleteThemesProfile(self, data):
        return self._apiDelete('projeto/configuracao/perfil_temas', 'perfil_temas_ids', data)

    def getLastCompletedActivities(self):
        return self._apiGet('acompanhamento/ultimas_atividades_finalizadas')

    def getRunningActivities(self):
        return self._apiGet('acompanhamento/atividades_em_execucao')

    def reshapeUT(self, workspacesId, reshapeGeom):
        response = self.httpPutJson(
            url="{0}/projeto/unidade_trabalho/reshape".format(self.getServer()),
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
            url="{0}/projeto/unidade_trabalho/cut".format(self.getServer()),
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
            url="{0}/projeto/unidade_trabalho/merge".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'merge_geom': mergeGeom
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def startLocalMode(self, activityId, userId):
        response = self.httpPutJson(
            url="{0}/gerencia/iniciar_modo_local".format(self.getServer()),
            postData={
                'atividade_id': activityId,
                'usuario_id': userId
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def exportToSAPLocal(self, activityData):
        pg = Postgresql(
            activityData['local_db']['database'],
            activityData['local_db']['username'],
            activityData['local_db']['host'],
            activityData['local_db']['port'],
            activityData['local_db']['password']
        )
        activityData['local_db']['host'] = 'localhost'
        try:
            pg.execute(
                '''
                    SELECT * FROM public.sap_local;
                ''',
                ()
            )
        except psycopg2.errors.UndefinedTable:
            raise Exception('Tabela "public.sap_local" não existe!')
            return
        result = pg.execute(
            '''
                SELECT count(*) FROM public.sap_local;
            ''',
            ()
        )
        if result[0][0] != 0:
            raise Exception('Há dados na tabela "public.sap_local"!')
            return
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
                activityData['dados']['atividade']['id'],
                json.dumps(activityData),
                activityData['dados']['atividade']['geom']
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

    def endLocalMode(self, dbData):
        pg = Postgresql(
            dbData['database'],
            dbData['username'],
            dbData['host'],
            dbData['port'],
            dbData['password']
        )
        result = pg.execute(
            '''
                SELECT
                    atividade_id,
                    data_inicio::text,
                    data_fim::text,
                    usuario_uuid 
                FROM public.sap_local;
            ''',
            ()
        )
        result = result[0]
        response = self.httpPutJson(
            url="{0}/gerencia/finalizar_modo_local".format(self.getServer()),
            postData={
                'atividade_id': result[0],
                'data_inicio': result[1],
                'data_fim': result[2],
                'usuario_uuid': result[3]
            },
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def createChangeReport(self, data):
        return self._apiCreate('gerencia/relatorio_alteracao', 'relatorio_alteracao', data)

    def deleteChangeReport(self, data):
        return self._apiDelete('gerencia/relatorio_alteracao', 'relatorio_alteracao_ids', data)

    def getChangeReport(self):
        return self._apiGet('gerencia/relatorio_alteracao')

    def updateChangeReport(self, data):
        return self._apiUpdate('gerencia/relatorio_alteracao', 'relatorio_alteracao', data)

    def resetPropertiesUT(self, data):
        return self._apiUpdate('gerencia/unidade_trabalho/propriedades', 'unidades_trabalho', data)

    def getRemotePluginsPath(self):
        response = self.httpGet(
            url="{0}/gerencia/plugin_path".format(self.getServer())
        )
        if response:
            return response.json()
        return {}

    def updateRemotePluginsPath(self, pluginPath):
        return self._apiUpdate('gerencia/plugin_path', 'plugin_path', pluginPath)

    def createProductLine(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/linha_producao".format(self.getServer()),
            postData=data,
            timeout=TIMEOUT
        )
        if response:
            return response.json()['message']
        return None

    def getProfileDifficultyType(self):
        return self._apiGet('projeto/tipo_perfil_dificuldade')

    def createProfileDifficulty(self, data):
        return self._apiCreate('projeto/configuracao/perfil_dificuldade_operador', 'perfis_dificuldade_operador', data)

    def deleteProfileDifficulty(self, data):
        return self._apiDelete('projeto/configuracao/perfil_dificuldade_operador', 'perfis_dificuldade_operador_ids', data)

    def getProfileDifficulty(self):
        return self._apiGet('projeto/configuracao/perfil_dificuldade_operador')

    def updateProfileDifficulty(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_dificuldade_operador', 'perfis_dificuldade_operador', data)

    def copySetupLot(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/lote/copiar".format(self.getServer()),
            postData=data
        )
        if response:
            return response.json()['message']
        return None

    def createWorkflows(self, data):
        return self._apiCreate('projeto/workflow', 'workflows', data)

    def deleteWorkflows(self, data):
        return self._apiDelete('projeto/workflow', 'workflows_ids', data)

    def getWorkflows(self):
        return self._apiGet('projeto/workflow')

    def updateWorkflows(self, data):
        return self._apiUpdate('projeto/workflow', 'workflows', data)

    def createWorkflowProfiles(self, data):
        return self._apiCreate('projeto/configuracao/perfil_workflow_dsgtools', 'perfil_workflow_dsgtools', data)

    def deleteWorkflowProfiles(self, data):
        return self._apiDelete('projeto/configuracao/perfil_workflow_dsgtools', 'perfil_workflow_dsgtools_ids', data)

    def getWorkflowProfiles(self):
        return self._apiGet('projeto/configuracao/perfil_workflow_dsgtools')

    def updateWorkflowProfiles(self, data):
        return self._apiUpdate('projeto/configuracao/perfil_workflow_dsgtools', 'perfil_workflow_dsgtools', data)

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
        return self._apiCreate('gerencia/fila_prioritaria', 'fila_prioritaria', data)

    def deleteFilaPrioritaria(self, data):
        return self._apiDelete('gerencia/fila_prioritaria', 'fila_prioritaria_ids', data)

    def getFilaPrioritaria(self):
        return self._apiGet('gerencia/fila_prioritaria')

    def updateFilaPrioritaria(self, data):
        return self._apiUpdate('gerencia/fila_prioritaria', 'fila_prioritaria', data)

    def getAtividadeSubfase(self):
        return self._apiGet('acompanhamento/atividade_subfase')
    
    ###############################
    def createPITs(self, data):
        return self._apiCreate('gerencia/pit', 'pit', data)

    def deletePITs(self, data):
        return self._apiDelete('gerencia/pit', 'pit_ids', data)

    def getPITs(self):
        return self._apiGet('gerencia/pit')

    def updatePITs(self, data):
        return self._apiUpdate('gerencia/pit', 'pit', data)
    
    def deleteProductsWithoutUT(self):
        try:
            response = self.httpDelete(
                url="{0}/perigo/produtos_sem_unidade_trabalho".format(self.getServer())
            )
            if response:
                return True, response.json()['message']
            return False, "Falha na requisição do servidor."
        except Exception as e:
            return False, f'Erro ao excluir produtos: {str(e)}'

    def deleteUTWithoutActivity(self):
        response = self.httpDelete(
            url="{0}/perigo/ut_sem_atividade".format(self.getServer())
        )
        if response:
            return response.json()['message']
        return []
    
    def deleteLoteWithoutProduct(self):
        try:
            response = self.httpDelete(
                url="{0}/perigo/lote_sem_produto".format(self.getServer())
            )
            if response:
                return True, response.json()['message']
            return False, "Falha na requisição do servidor."
        except Exception as e:
            return False, f'Erro ao excluir lotes: {str(e)}'
    
    def relatorioAtividades(self, data_inicio, data_fim):
        return self._apiGet('rh/atividades_por_periodo/{0}/{1}'.format(data_inicio, data_fim))

    def relatorioAtividadeByUsers(self, user_id, data_inicio, data_fim):
        return self._apiGet('rh/atividades_por_usuario_e_periodo/{0}/{1}/{2}'.format(user_id, data_inicio, data_fim))

    def relatorioByLots(self, data_inicio, data_fim):
        return self._apiGet('rh/lote_stats/{0}/{1}'.format(data_inicio, data_fim))

    def getResumoUsuario(self):
        response = self.httpGet(
            url="{0}/acompanhamento/resumo_usuario".format(self.getServer())
        )
        if response:
            return response.json().get('dados', [])
        return []
    
    def getAlteracaoFluxo(self):
        response = self.httpGet(
            url="{0}/gerencia/alteracao_fluxo".format(self.getServer())
        )
        if response:
            return response.json().get('dados', [])
        return []

    def atualizaAlteracaoFluxo(self, data):
        return self._apiUpdate('gerencia/alteracao_fluxo', 'alteracao_fluxo', data)

    def deleteProducts(self, productsIds):
        return self._apiDelete('projeto/produto', 'produto_ids', productsIds)
    
    ## Funções para o módulo de campo
    def getSituacoes(self):
        return self._apiGet('campo/situacao')

    def getCategorias(self):
        return self._apiGet('campo/categoria')
    
    def getProdutosByLot(self, lot_id):
        return self._apiGet('campo/produtos/{0}'.format(lot_id))

    def getCampos(self):
        return self._apiGet('campo/campos')
    
    def criaCampo(self, campo):
        data = {
            "campo": campo 
            }
        response = self.httpPostJson(
            url=f"{self.getServer()}/campo/campos",
            postData=data
            )
        if response:
            return response.json()['dados']
        return []
    
    def atualizaCampo(self, id, campo_data):
        response = self.httpPutJson(
            url="{0}/campo/campos/{1}".format(self.getServer(), id),
            postData={
                'campo': campo_data
            }
        )
        if response:
            return response.json()
        return None
    
    def deletaCampo(self, id):
        return self._apiDelete('campo/campos/{0}'.format(id), 'id', id)

    def getFotos(self):
        return self._apiGet('campo/fotos')
    
    def getFotosByCampo(self, campo_id):
        response = self.httpGet(
            url=f"{self.getServer()}/campo/fotos/{campo_id}"
        )
        if response:
            return response.json()['dados']
        return
    
    def getFotoById(self, id):
        response = self.httpGet(url="{0}/campo/fotos/{1}".format(self.getServer(), id))
        if response:
            return response.json()['dados']
        return None
    
    def criaFotos(self, fotos):
        response = self.httpPostJson(
            url=f"{self.getServer()}/campo/fotos",
            postData=fotos
        )
        if response:
            return response.json()['dados']
        return []
    
    def atualizaFoto(self, id, foto_data):
        return self._apiUpdate('campo/fotos/{0}'.format(id), 'foto', foto_data)

    def deletaFoto(self, id):
        return self._apiDelete('campo/fotos/{0}'.format(id), 'id', id)

    def getTracks(self):
        return self._apiGet('campo/tracks')
    
    def getTracksByCampo(self, campo_id):
        response = self.httpGet(
            url=f"{self.getServer()}/campo/tracks/{campo_id}"
        )  
        if response:
            return response.json()['message']
        return []
    
    def criaTracker(self, track_data):
        response = self.httpPostJson(
            url="{0}/campo/tracks".format(self.getServer()),
            postData={
                "track": track_data
            }
        )
        if response:
            return response.json()['dados']
        return None

    def atualizaTracker(self, id, track_data):
        return self._apiUpdate('campo/tracks/{0}'.format(id), 'track', track_data)

    def deletaTracker(self, id):
        return self._apiDelete('campo/tracks/{0}'.format(id), 'id', id)
    
    def criaTrackerPonto(self, tracks_ponto):
        """
        Envia pontos de track para o backend.

        Parameters:
        tracks_ponto (list): Lista de dicionários contendo os dados dos pontos do tracker

        Returns:
        list: Lista de IDs dos pontos criados no banco de dados
        """
        # Envia a requisição POST para o backend diretamente com a lista de pontos
        # Sem encapsular em outro objeto
        response = self.httpPostJson(
            url=f"{self.getServer()}/campo/tracks_ponto",
            postData=tracks_ponto
        )

        # Processa a resposta
        if response:
            return response.json()['dados']['ids']
        return []

    def getProdutosCampo(self):
        return self._apiGet('campo/produtos_campo')

    def getProdutosByCampoId(self, campo_id):
        return self._apiGet('campo/produtos_campo/{0}'.format(campo_id))
    
    def criaProdutosCampo(self, associacoes):
        return self._apiCreate('campo/produtos_campo', 'associacoes', associacoes)
    
    def deletaProdutoByCampoId(self, campo_id):
        response = self.httpDelete(
            url = f"{self.getServer()}/campo/produtos_campo/{campo_id}"
        )
        if response:
            return response.json()['message']
        return []