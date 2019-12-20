import json, requests, socket


class ApiSapHttp:   

    def __init__(self):
        self.server = None
        self.token = None

    def checkConnection(self):
        response = { '_erro' : ''}
        session = requests.Session()
        session.trust_env = False
        session.get(self.server, timeout=8)

    def setServer(self, server):
        self.server = server

    def setToken(self, token):
        self.token = token
    
    def getSapProfiles(self):
        response = self.httpGet(
            url="{0}/gerencia/perfil_producao".format(self.server)
        )
        if response:
            profiles = response.json()['dados']
            return profiles
        return [{'nome': 'Sem perfis de produção', 'id': False}]

    def getSapUsers(self):
        response = self.httpGet(
            url="{0}/projeto/usuarios".format(self.server)
        )
        if response:
            users = response.json()['dados']
            return users
        return [{'nome': 'Sem usuários', 'id': False}]

    def loginAdminUser(self, user, password, gisVersion, pluginsVersion):
        response = self.httpPostJson(
            url="{0}/login".format(self.server), 
            postData={
                "usuario" : user,
                "senha" : password,
                'plugins' : pluginsVersion,
                'qgis' : gisVersion,
                'cliente' : 'qgis'
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
        self.checkConnection()
        header = {
            'content-type' : 'application/json'
        }
        if self.token:
            header['authorization'] = self.token
        session = requests.Session()
        session.trust_env = False
        response = session.post(url, data=json.dumps(postData), headers=header)
        if not response.ok:
            raise Exception(str(response.text))
        return response

    def httpGet(self, url): 
        self.checkConnection()
        header = {
            'authorization' : self.token
        }
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, headers=header)
        if not response.ok:
            raise Exception(str(response.text))
        return response

    def addNewRevision(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/criar_revisao".format(self.server),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']

    def addNewRevisionCorrection(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/criar_revcorr".format(self.server),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']
    
    def advanceActivityToNextStep(self, activityIds, endStep):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/avancar".format(self.server),
            postData={
                "atividade_ids" : activityIds,
                "concluida" : endStep
            }
        )
        return response.json()['message']

    def createPriorityGroupActivity(self, activityIds, priority, profileId):
        response = self.httpPostJson(
            url="{0}/gerencia/fila_prioritaria_grupo".format(self.server),
            postData={
                "atividade_ids" : activityIds,
                "prioridade" : int(priority),
                "perfil_producao_id" : profileId
            }
        )
        return response.json()['message']

    #interface
    def fillCommentActivity(self, activityIds, commentActivity, commentWorkspace, commentStep, commentSubfase):
        response = self.httpPostJson(
            url="{0}/gerencia/observacao".format(self.server),
            postData={
                "atividade_ids" : activityIds,
                "observacao_atividade" : commentActivity,
                "observacao_unidade_trabalho" : commentWorkspace,
                "observacao_etapa" : commentStep,
                "observacao_subfase" : commentSubfase
            }
        )
        return response.json()['message']

    def openActivity(self):
        pass
        
    #interface
    def lockWorkspace(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/unidade_trabalho/disponivel".format(self.server),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : False
            }
        )
        return response.json()['message']

    #interface
    def openNextActivityByUser(self, userId):
        response = self.httpGet(
            url="{0}/gerencia/atividade/usuario/{1}".format(self.server, userId)
        )
        return response.json()['message']

    #interface
    def pauseActivity(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/pausar".format(self.server),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']
    
    #interface
    def restartActivity(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/reiniciar".format(self.server),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']
    
    #interface
    def returnActivityToPreviousStep(self, activityIds, preserveUser):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/voltar".format(self.server),
            postData={
                "atividade_ids" : activityIds,
                "manter_usuarios" : preserveUser
            }
        )
        return response.json()['message']

    #interface
    def setPriorityActivity(self, activityIds, priority, userId):
        response = self.httpPostJson(
            url="{0}/gerencia/fila_prioritaria".format(self.server),
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
            url="{0}/gerencia/unidade_trabalho/disponivel".format(self.server),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : True
            }
        )
        return response.json()['message']

    def getSapStyles(self):
        response = self.httpGet(
            url="{0}/projeto/estilos".format(self.server)
        )
        if response:
            styles = response.json()['dados']
            return styles
        return []

    def setSapStyles(self, stylesData):
        response = self.httpPostJson(
            url="{0}/projeto/estilos".format(self.server),
            postData={
                "estilos" : stylesData,
            }
        )
        return response.json()['message']

    def getSapModels(self):
        response = self.httpGet(
            url="{0}/projeto/modelos".format(self.server)
        )
        if response:
            styles = response.json()['dados']
            return styles
        return []

    def setSapModels(self, modelsData):
        response = self.httpPostJson(
            url="{0}/projeto/modelos".format(self.server),
            postData={
                "modelos" : modelsData,
            }
        )
        return response.json()['message']

    def getSapRules(self):
        response = self.httpGet(
            url="{0}/projeto/regras".format(self.server)
        )
        if response:
            styles = response.json()['dados']
            return styles
        return []

    def setSapRules(self, rulesData):
        response = self.httpPostJson(
            url="{0}/projeto/regras".format(self.server),
            postData={
                "regras" : rulesData,
            }
        )
        return response.json()['message']
    

        
        