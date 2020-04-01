import json, requests, socket

from Ferramentas_Gerencia.sap.interfaces.ISapApi import ISapApi


class SapHttp(ISapApi):   

    def __init__(self):
        super(SapHttp, self).__init__()
        self.server = None
        self.token = None

    def checkConnection(self, server):
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
    
    def getProfiles(self):
        response = self.httpGet(
            url="{0}/gerencia/perfil_producao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return [{'nome': 'Sem perfis de produção', 'id': False}]

    def getUsers(self):
        response = self.httpGet(
            url="{0}/usuarios".format(self.getServer())
        )
        if response:
            return response.json()['dados']
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
        if not self.validVersion(responseJson):
            raise Exception("Versão do servidor sap errada")
        if not self.isAdminUser(responseJson):
            raise Exception("Usuário não é administrador")
        return responseJson

    def validVersion(self, responseJson):
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

    def checkError(self, response):
        if not response.ok:
            raise Exception(response.json()['message'])
    
    def httpPost(self, url, postData, headers):
        if self.getToken():
            headers['authorization'] = self.getToken()
        session = requests.Session()
        session.trust_env = False
        response = session.post(url, data=json.dumps(postData), headers=headers)
        self.checkError(response)
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
        self.checkError(response)
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
        self.checkError(response)
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
        self.checkError(response)
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
            url="{0}/projeto/atividade/criar_revisao".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']

    def addNewRevisionCorrection(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/projeto/atividade/criar_revcorr".format(self.getServer()),
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

    def openActivity(self, activityId):
        response = self.httpGet(
            url="{0}/gerencia/atividade/{1}".format(self.getServer(), activityId),
        )
        return response.json()

    #interface
    def openNextActivityByUser(self, userId, nextActivity):
        params = '?proxima=true' if nextActivity else ''
        response = self.httpGet(
            url="{0}/gerencia/atividade/usuario/{1}{2}".format(self.getServer(), userId, params)
        )
        return response.json()
        
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

    def getStyles(self):
        response = self.httpGet(
            url="{0}/projeto/estilos".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateStyles(self, stylesData):
        response = self.httpPostJson(
            url="{0}/projeto/estilos".format(self.getServer()),
            postData={
                "estilos" : stylesData,
            }
        )
        return response.json()['message']

    def getModels(self):
        response = self.httpGet(
            url="{0}/projeto/modelos".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateModels(self, modelsData):
        response = self.httpPostJson(
            url="{0}/projeto/modelos".format(self.getServer()),
            postData={
                "modelos" : modelsData,
            }
        )
        return response.json()['message']

    def getRules(self):
        response = self.httpGet(
            url="{0}/projeto/regras".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateRules(self, rulesData, groupsData):
        response = self.httpPostJson(
            url="{0}/projeto/regras".format(self.getServer()),
            postData={
                'regras': rulesData,
                'grupo_regras': groupsData
            }
        )
        return response.json()['message']

    def getQgisProject(self):
        response = self.httpGet(
            url="{0}/projeto/projeto_qgis".format(self.getServer())
        )
        if response:
            return response.json()['dados']['projeto']
        return []

    def getLayersQgisProject(self, projectInProgress):
        params = '?em_andamento=true' if projectInProgress else ''
        response = self.httpGet(
            url="{0}/gerencia/view_acompanhamento{1}".format(self.getServer(), params)
        )
        if response:
            return response.json()['dados']
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
            return response.json()['dados']
        return []
        
    def importUsersAuthService(self, usersIds):
        response = self.httpPostJson(
            url="{0}/usuarios".format(self.getServer()),
            postData={
                'usuarios': usersIds,
            }
        )
        return response.json()['message']

    def updateUsersPrivileges(self, usersData):
        response = self.httpPutJson(
            url="{0}/usuarios".format(self.getServer()),
            postData={
                'usuarios': usersData
            }    
        )
        return response.json()['message']

    def deleteActivities(self, activityIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/atividades".format(self.getServer()),
            postData={
                'atividades_ids': activityIds
            }    
        )
        return response.json()['message']
    
    def createActivities(self, workspacesIds, stepId):
        response = self.httpPostJson(
            url="{0}/projeto/atividades".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'etapa_id': stepId
            }    
        )
        return response.json()['message']

    def getDatabases(self):
        response = self.httpGet(
            url="{0}/projeto/banco_dados".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getLayers(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/camadas".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getAuthDatabase(self):
        response = self.httpGet(
            url="{0}/projeto/login".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def resetPrivileges(self):
        response = self.httpPut(
            url="{0}/gerencia/atividades/permissoes".format(self.getServer())
        )
        return response.json()['message']

    def importLayers(self, layersImported):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/camadas".format(self.getServer()),
            postData={
                'camadas': layersImported
            }    
        )
        return response.json()['message']

    def getLayers(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/camadas".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def deleteLayers(self, layersIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/camadas".format(self.getServer()),
            postData={
                'camadas_ids': layersIds
            }    
        )
        return response.json()['message']

    def updateLayers(self, layersData):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/camadas".format(self.getServer()),
            postData={
                'camadas': layersData
            }    
        )
        return response.json()['message']

    def getLots(self):
        response = self.httpGet(
            url="{0}/projeto/lote".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def alterLot(self, workspacesIds, lotId):
        response = self.httpPutJson(
            url="{0}/projeto/unidade_trabalho/lote".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'lote_id': lotId
            }    
        )
        return response.json()['message']

    def revokePrivileges(self, dbHost, dbPort, dbName):
        response = self.httpPostJson(
            url="{0}/gerencia/banco_dados/revogar_permissoes".format(self.getServer()),
            postData={
                "servidor" : dbHost,
                "porta" : int(dbPort),
                "banco" : dbName
            }
        )
        return response.json()['message']

    def getMenus(self):
        response = self.httpGet(
            url="{0}/projeto/menus".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getFmeServers(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/gerenciador_fme".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createFmeServers(self, fmeServers):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/gerenciador_fme".format(self.getServer()),
            postData={
                'gerenciador_fme': fmeServers
            }   
        )
        return response.json()['message']

    def updateFmeServers(self, fmeServers):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/gerenciador_fme".format(self.getServer()),
            postData={
                'gerenciador_fme': fmeServers
            } 
        )
        return response.json()['message']

    def deleteFmeServers(self, fmeServersIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/gerenciador_fme".format(self.getServer()),
            postData={
                'servidores_id': fmeServersIds
            }  
        )
        return response.json()['message']

    def getFmeProfiles(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/perfil_fme".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createFmeProfiles(self, fmeProfiles):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/perfil_fme".format(self.getServer()),
            postData={
                'perfis_fme': fmeProfiles
            }   
        )
        return response.json()['message']

    def updateFmeProfiles(self, fmeProfiles):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/perfil_fme".format(self.getServer()),
            postData={
                'perfis_fme': fmeProfiles
            } 
        )
        return response.json()['message']

    def deleteFmeProfiles(self, fmeProfilesIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/perfil_fme".format(self.getServer()),
            postData={
                'perfil_fme_ids': fmeProfilesIds
            }  
        )
        return response.json()['message']

    def getSubphases(self):
        response = self.httpGet(
            url="{0}/projeto/subfases".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getSteps(self):
        response = self.httpGet(
            url="{0}/projeto/etapas".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def deleteUserActivities(self, userId):
        response = self.httpDelete(
            url="{0}/perigo/atividades/usuario/{1}".format(self.getServer(), userId)
        )
        if response:
            return response.json()['message']
        return []

    def getInputGroups(self):
        response = self.httpGet(
            url="{0}/projeto/grupo_insumo".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def deleteAssociatedInputs(self, workspacesIds, inputGroupId):
        response = self.httpDeleteJson(
            url="{0}/projeto/insumos".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'grupo_insumo_id': inputGroupId
            }  
        )
        return response.json()['message']

    def deleteWorkUnits(self, workspacesIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/unidade_trabalho".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds
            }  
        )
        return response.json()['message']

    def deleteRevisionCorrection(self, stepId):
        response = self.httpDelete(
            url="{0}/projeto/revisao/{1}".format(self.getServer(), stepId)
        )
        if response:
            return response.json()['message']
        return []

    def getProductionLines(self):
        response = self.httpGet(
            url="{0}/projeto/linhas_producao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createProducts(self, productionLineId, products):
        response = self.httpPostJson(
            url="{0}/projeto/produto".format(self.getServer()),
            postData={
                'linha_producao_id': productionLineId,
                'produtos': products
            }   
        )
        return response.json()['message']

    def getAssociationStrategies(self):
        response = self.httpGet(
            url="{0}/projeto/estrategia_associacao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

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
        return response.json()['message']

    def loadWorkUnit(self, subphaseId, workUnits):
        response = self.httpPostJson(
            url="{0}/projeto/unidade_trabalho".format(self.getServer()),
            postData={
                'subfase_id': subphaseId,
                'unidades_trabalho': workUnits
            }   
        )
        return response.json()['message']

    def getProductionData(self):
        response = self.httpGet(
            url="{0}/projeto/dado_producao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def copyWorkUnit(self, workspacesIds, stepsIds, associateInputs):
        response = self.httpPostJson(
            url="{0}/projeto/unidade_trabalho/copiar".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'etapa_ids': stepsIds,
                'associar_insumos': associateInputs
            }   
        )
        return response.json()['message']