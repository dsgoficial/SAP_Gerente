import json, requests, socket

from Ferramentas_Gerencia.sap.interfaces.ISapApi import ISapApi


class SapApiHttp(ISapApi):   

    def __init__(self):
        super(SapApiHttp, self).__init__()
        self.server = None
        self.token = None

    def checkConnection(self, server):
        response = { '_erro' : ''}
        session = requests.Session()
        session.trust_env = False
        session.get(server, timeout=8)

    def setServer(self, server):
        self.server = "{0}/api".format(server)

    def getServer(self):
        return self.server

    def setToken(self, token):
        self.token = token

    def getToken(self):
        return self.token
    
    def getSapProfiles(self):
        response = self.httpGet(
            url="{0}/gerencia/perfil_producao".format(self.getServer())
        )
        if response:
            profiles = response.json()['dados']
            return profiles
        return [{'nome': 'Sem perfis de produção', 'id': False}]

    def getSapUsers(self):
        response = self.httpGet(
            url="{0}/usuarios".format(self.getServer())
        )
        if response:
            users = response.json()['dados']
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
        responseJson = response.json()
        if not self.validSapVersion(responseJson):
            raise Exception("Versão do servidor sap errada")
        if not self.isAdminUser(responseJson):
            raise Exception("Usuário não é administrador")
        return responseJson

    def validSapVersion(self, responseJson):
        return ('version' in responseJson and responseJson['version'].split('.')[0] == '2')

    def isAdminUser(self, responseJson):
        return ('administrador' in responseJson['dados'] and responseJson['dados']['administrador'])

    def httpPostJson(self, url, postData):
        self.checkConnection(
            self.getServer()
        )
        headers = {
            'content-type' : 'application/json'
        }
        return  self.httpPost(
            url, 
            postData,
            headers
        )
    
    def httpPost(self, url, postData, headers):
        if self.getToken():
            headers['authorization'] = self.getToken()
        session = requests.Session()
        session.trust_env = False
        response = session.post(url, data=json.dumps(postData), headers=headers)
        if not response.ok:
            raise Exception(str(response.text))
        return response

    def httpGet(self, url): 
        self.checkConnection(
            self.getServer()
        )
        headers = {}
        if self.getToken():
            headers['authorization'] = self.getToken()
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, headers=headers)
        if not response.ok:
            raise Exception(str(response.text))
        return response

    def httpPut(self, url, postData={}, headers={}):
        self.checkConnection(
            self.getServer()
        )
        if self.getToken():
            headers['authorization'] = self.getToken()
        session = requests.Session()
        session.trust_env = False
        response = session.put(url, data=json.dumps(postData), headers=headers)
        if not response.ok:
            raise Exception(str(response.text))
        return response

    def httpPutJson(self, url, postData):
        self.checkConnection(
            self.getServer()
        )
        headers = {
            'content-type' : 'application/json'
        }
        return  self.httpPut(
            url, 
            postData,
            headers
        )

    def httpDelete(self, url, postData={}, headers={}):
        self.checkConnection(
            self.getServer()
        )
        if self.getToken():
            headers['authorization'] = self.getToken()
        session = requests.Session()
        session.trust_env = False
        response = session.delete(url, data=json.dumps(postData), headers=headers)
        if not response.ok:
            raise Exception(str(response.text))
        return response

    def httpDeleteJson(self, url, postData):
        self.checkConnection(
            self.getServer()
        )
        headers = {
            'content-type' : 'application/json'
        }
        return  self.httpDelete(
            url, 
            postData,
            headers
        )

    def addNewRevision(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/criar_revisao".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']

    def addNewRevisionCorrection(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/criar_revcorr".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']
    
    def advanceActivityToNextStep(self, activityIds, endStep):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/avancar".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "concluida" : endStep
            }
        )
        return response.json()['message']

    def createPriorityGroupActivity(self, activityIds, priority, profileId):
        response = self.httpPostJson(
            url="{0}/gerencia/fila_prioritaria_grupo".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "prioridade" : int(priority),
                "perfil_producao_id" : profileId
            }
        )
        return response.json()['message']

    #interface
    def fillCommentActivity(self, activityIds, commentActivity, commentWorkspace, commentStep, commentSubfase, commentLot):
        response = self.httpPostJson(
            url="{0}/gerencia/observacao".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "observacao_atividade" : commentActivity,
                "observacao_unidade_trabalho" : commentWorkspace,
                "observacao_etapa" : commentStep,
                "observacao_subfase" : commentSubfase,
                "observacao_lote" : commentLot
            }
        )
        return response.json()['message']

    def getCommentsByActivity(self, activityId):
        response = self.httpGet(
            url="{0}/gerencia/atividade/{1}/observacao".format(self.getServer(), activityId)
        )
        return response.json()['dados']

    def openActivity(self):
        pass
        
    #interface
    def lockWorkspace(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/unidade_trabalho/disponivel".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : False
            }
        )
        return response.json()['message']

    #interface
    def openNextActivityByUser(self, userId, nextActivity):
        params = '?proxima=true' if nextActivity else ''
        response = self.httpGet(
            url="{0}/gerencia/atividade/usuario/{1}{2}".format(self.getServer(), userId, params)
        )
        return response.json()['message']

    #interface
    def pauseActivity(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/pausar".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']
    
    #interface
    def restartActivity(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/reiniciar".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']
    
    #interface
    def returnActivityToPreviousStep(self, activityIds, preserveUser):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/voltar".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "manter_usuarios" : preserveUser
            }
        )
        return response.json()['message']

    #interface
    def setPriorityActivity(self, activityIds, priority, userId):
        response = self.httpPostJson(
            url="{0}/gerencia/fila_prioritaria".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "prioridade" : int(priority),
                "usuario_prioridade_id" : userId
            }
        )
        return response.json()['message']

     #interface
    def unlockWorkspace(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/unidade_trabalho/disponivel".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : True
            }
        )
        return response.json()['message']

    def getSapStyles(self):
        response = self.httpGet(
            url="{0}/projeto/estilos".format(self.getServer())
        )
        if response:
            styles = response.json()['dados']
            return styles
        return []

    def setSapStyles(self, stylesData):
        response = self.httpPostJson(
            url="{0}/projeto/estilos".format(self.getServer()),
            postData={
                "estilos" : stylesData,
            }
        )
        return response.json()['message']

    def getSapModels(self):
        response = self.httpGet(
            url="{0}/projeto/modelos".format(self.getServer())
        )
        if response:
            styles = response.json()['dados']
            return styles
        return []

    def setSapModels(self, modelsData):
        response = self.httpPostJson(
            url="{0}/projeto/modelos".format(self.getServer()),
            postData={
                "modelos" : modelsData,
            }
        )
        return response.json()['message']

    def getSapRules(self):
        response = self.httpGet(
            url="{0}/projeto/regras".format(self.getServer())
        )
        if response:
            styles = response.json()['dados']
            return styles
        return []

    def setSapRules(self, rulesData, groupsData):
        response = self.httpPostJson(
            url="{0}/projeto/regras".format(self.getServer()),
            postData={
                'regras': rulesData,
                'grupo_regras': groupsData
            }
        )
        return response.json()['message']

    def createWorkUnit(self, inputData):
        pass  
    
    def getQgisProject(self):
        response = self.httpGet(
            url="{0}/projeto/projeto_qgis".format(self.getServer())
        )
        if response:
            project = response.json()['dados']['projeto']
            return project
        return []

    def getLayersQgisProject(self, projectInProgress):
        params = '?em_andamento=true' if projectInProgress else ''
        response = self.httpGet(
            url="{0}/gerencia/view_acompanhamento{1}".format(self.getServer(), params)
        )
        if response:
            layers = response.json()['dados']
            return layers
        return []

    def updateBlockedActivities(self):
        response = self.httpPut(
            url="{0}/gerencia/atividades_bloqueadas".format(self.getServer())
        )
        return response.json()['message']

    def synchronizeUserInformation(self):
        response = self.httpPut(
            url="{0}/usuarios/sincronizar".format(self.getServer())
        )
        return response.json()['message']

    def getUsersFromAuthService(self):
        response = self.httpGet(
            url="{0}/usuarios/servico_autenticacao".format(self.getServer())
        )
        if response:
            users = response.json()['dados']
            return users
        return []
        
    def importUsersAuthService(self, usersIds):
        response = self.httpPostJson(
            url="{0}/usuarios".format(self.getServer()),
            postData={
                'usuarios': usersIds,
            }
        )
        return response.json()['message']

    def setUsersPrivileges(self, usersData):
        response = self.httpPutJson(
            url="{0}/usuarios".format(self.getServer()),
            postData={
                'usuarios': usersData
            }    
        )
        return response.json()['message']

    def deleteActivities(self, layersIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/atividades".format(self.getServer()),
            postData={
                'atividades_ids': layersIds
            }    
        )
        return response.json()['message']
        