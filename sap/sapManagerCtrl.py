import os

from Ferramentas_Gerencia.sap.interfaces.ISapCtrl import ISapCtrl

from Ferramentas_Gerencia.sap.factory.sapApiSingleton import SapApiSingleton
from Ferramentas_Gerencia.sap.factory.functionsSettingsSingleton import FunctionsSettingsSingleton
from Ferramentas_Gerencia.sap.factory.managementDockBuilder import ManagementDockBuilder
from Ferramentas_Gerencia.sap.factory.dockDirector import DockDirector
from Ferramentas_Gerencia.sap.factory.loginSingleton import LoginSingleton
from Ferramentas_Gerencia.sap.factory.managementStylesSingleton  import ManagementStylesSingleton
from Ferramentas_Gerencia.sap.factory.managementModelsSingleton  import ManagementModelsSingleton
from Ferramentas_Gerencia.sap.factory.managementFmeServersSingleton  import ManagementFmeServersSingleton
from Ferramentas_Gerencia.sap.factory.managementFmeProfilesSingleton  import ManagementFmeProfilesSingleton
from Ferramentas_Gerencia.sap.factory.managementRulesSingleton  import ManagementRulesSingleton
from Ferramentas_Gerencia.sap.factory.managementRuleSetSingleton  import ManagementRuleSetSingleton
from Ferramentas_Gerencia.sap.factory.managementUsersPrivilegesSingleton  import ManagementUsersPrivilegesSingleton
from Ferramentas_Gerencia.sap.factory.managementEditLayersSingleton  import ManagementEditLayersSingleton
from Ferramentas_Gerencia.sap.factory.managementImportLayersSingleton  import ManagementImportLayersSingleton
from Ferramentas_Gerencia.sap.factory.addStyleFormSingleton  import AddStyleFormSingleton
from Ferramentas_Gerencia.sap.factory.addModelFormSingleton  import AddModelFormSingleton
from Ferramentas_Gerencia.sap.factory.addRuleFormSingleton  import AddRuleFormSingleton
from Ferramentas_Gerencia.sap.factory.addRuleSetFormSingleton  import AddRuleSetFormSingleton
from Ferramentas_Gerencia.sap.factory.addRulesCsvFormSingleton  import AddRulesCsvFormSingleton
from Ferramentas_Gerencia.sap.factory.addFmeServerFormSingleton  import AddFmeServerFormSingleton
from Ferramentas_Gerencia.sap.factory.addFmeProfileFormSingleton  import AddFmeProfileFormSingleton
from Ferramentas_Gerencia.sap.factory.rulesSingleton  import RulesSingleton
from Ferramentas_Gerencia.sap.factory.databasesFactoryMethod  import DatabasesFactoryMethod

class SapManagerCtrl(ISapCtrl):

    def __init__(self, gisPlatform, fmeCtrl):
        super(SapManagerCtrl, self).__init__(gisPlatform, fmeCtrl)
        self.loginView = LoginSingleton.getInstance(loginCtrl=self)
        self.apiSap = SapApiSingleton.getInstance()
        self.dockSap = None

    def loadDockSap(self):
        dockDirector = DockDirector()
        managementDockBuilder = ManagementDockBuilder()
        dockDirector.constructSapManagementDock(managementDockBuilder, sapCtrl=self)
        self.dockSap = managementDockBuilder.getResult()
        self.gisPlatform.addDockWidget(self.dockSap)

    #interface
    def showLoginView(self):
        self.loginView.loadData(
            user=self.gisPlatform.getSettingsVariable('sapmanager:user'), 
            server=self.gisPlatform.getSettingsVariable('sapmanager:server')
        )
        self.loginView.showView()

    def saveLoginData(self, user, password, server):
        self.gisPlatform.setSettingsVariable('sapmanager:user', user)
        self.gisPlatform.setSettingsVariable('sapmanager:password', password)
        self.gisPlatform.setSettingsVariable('sapmanager:server', server)

    #interface
    def authUser(self, user, password, server):
        try:
            self.apiSap.setServer(server)
            response = self.apiSap.loginAdminUser(
                user, 
                password,
                self.gisPlatform.getVersion(),
                self.gisPlatform.getPluginsVersions()
            )
            self.apiSap.setToken(response['dados']['token'])
            self.loadDockSap()
            self.loginView.closeView()      
        except Exception as e:
            self.loginView.showError('Aviso', str(e))
        finally:
            self.saveLoginData(user, password, server)
            
    #interface
    def getSapUsers(self):
        try:
            return self.apiSap.getUsers()
        except Exception as e:
            self.loginView.showError('Aviso', str(e))
            return []

    #interface
    def getSapProfiles(self):
        try:
            return self.apiSap.getProfiles()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def getValuesFromLayer(self, functionName, fieldName):
        functionSettings = FunctionsSettingsSingleton.getInstance()
        fieldSettings = functionSettings.getSettings(functionName, fieldName)
        try:
            for layerOptions in fieldSettings:
                values = self.gisPlatform.getFieldValuesFromLayer(
                    layerOptions['layerName'],
                    layerOptions['fieldName'],
                    layerOptions['allSelection'],
                    layerOptions['chooseAttribute']
                )
                if values:
                    break
            return ",".join([ str(fid) for fid in values ])
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return ''

    def getFeatureAttributes(self):
        pass

    #interface
    def addNewRevision(self, activityIds):
        try:
            message = self.apiSap.addNewRevision(
                activityIds
            )
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    #interface
    def addNewRevisionCorrection(self, activityIds):
        try:
            message = self.apiSap.addNewRevisionCorrection(
                activityIds
            )
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    #interface
    def advanceActivityToNextStep(self, activityIds, endStep):
        try:
            message = self.apiSap.advanceActivityToNextStep(
                activityIds, 
                endStep
            )
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def createWorkUnit(self, layerName, size, overlay, deplace, prefixName, onlySelected):
        try:
            self.gisPlatform.generateWorkUnit(
                layerName, size, overlay, deplace, prefixName, onlySelected
            )
            self.dockSap.showInfo('Aviso', 'Unidades de trabalho geradas com sucesso!')
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    #interface
    def createPriorityGroupActivity(self, activityIds, priority, profileId):
        try:
            message = self.apiSap.createPriorityGroupActivity(
                activityIds, 
                priority, 
                profileId
            )
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    #interface
    def fillCommentActivity(self, activityIds, commentActivity, commentWorkspace, commentStep, commentSubfase, commentLot):
        try:
            message = self.apiSap.fillCommentActivity(
                activityIds, 
                commentActivity, 
                commentWorkspace, 
                commentStep, 
                commentSubfase,
                commentLot
            )
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def getCommentsByActivity(self, activityId):
        return self.apiSap.getCommentsByActivity(activityId)
        
    #interface
    def lockWorkspace(self, workspacesIds):
        try:
            message = self.apiSap.lockWorkspace(workspacesIds)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def openActivity(self, activityIds):
        try:
            acitivityData = self.apiSap.openActivity(activityIds)
            acitivityData['token'] = self.apiSap.getToken()
            acitivityData['server'] = self.gisPlatform.getSettingsVariable('sapmanager:server') 
            acitivityData['user'] = self.gisPlatform.getSettingsVariable('sapmanager:user')
            acitivityData['password'] = self.gisPlatform.getSettingsVariable('sapmanager:password')
            self.gisPlatform.startSapFP(acitivityData)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    #interface
    def openNextActivityByUser(self, userId, nextActivity):
        try:
            acitivityData = self.apiSap.openNextActivityByUser(userId, nextActivity)
            acitivityData['token'] = self.apiSap.getToken()
            acitivityData['server'] = self.gisPlatform.getSettingsVariable('sapmanager:server') 
            acitivityData['user'] = self.gisPlatform.getSettingsVariable('sapmanager:user')
            acitivityData['password'] = self.gisPlatform.getSettingsVariable('sapmanager:password')
            self.gisPlatform.startSapFP(acitivityData)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    #interface
    def pauseActivity(self, workspacesIds):
        try:
            message = self.apiSap.pauseActivity(workspacesIds)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
    
    #interface
    def restartActivity(self, workspacesIds):
        try:
            message = self.apiSap.restartActivity(workspacesIds)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
    
    #interface
    def returnActivityToPreviousStep(self, activityIds, preserveUser):
        try:
            message = self.apiSap.returnActivityToPreviousStep(activityIds, preserveUser)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    #interface
    def setPriorityActivity(self, activityIds, priority, userId):
        try:
            message = self.apiSap.setPriorityActivity(activityIds, priority, userId)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

     #interface
    def unlockWorkspace(self, workspacesIds):
        try:
            message = self.apiSap.unlockWorkspace(workspacesIds)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def updateBlockedActivities(self):
        try:
            message = self.apiSap.updateBlockedActivities()
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    #interface
    def getSapStyles(self):
        try:
            return self.apiSap.getStyles()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def openManagementStyles(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        if managementStyles.isVisible():
            managementStyles.toTopLevel()
            return
        self.loadManagementDialogData(managementStyles, self.apiSap.getStyles())
        managementStyles.show()
        
    def loadStylesFromLayersSelection(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        stylesData = self.gisPlatform.getQmlStyleFromLayersTreeSelection()
        if len(stylesData) == 0:
            managementStyles.showError('Aviso', "Selecione no mínimo uma camada.")
            return
        addStyleForm = AddStyleFormSingleton.getInstance(parent=managementStyles)
        if not addStyleForm.exec():
            return
        stylesRows = []
        styleName = addStyleForm.getData()['styleName']
        for styleData in stylesData:
            managementStyles.addRow(
                styleData['f_table_schema'],
                styleData['f_table_name'],
                styleName,
                styleData['styleqml'],
                styleData['stylesld'],
                styleData['ui'],
                styleData['f_geometry_column']
            )

    def applyStylesOnLayers(self, stylesData):
        self.gisPlatform.applyStylesOnLayers(stylesData)

    def updateSapStyles(self, stylesData):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        try:
            message = self.apiSap.updateStyles(stylesData)
            managementStyles.showInfo('Aviso', message)
        except Exception as e:
            managementStyles.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementStyles, self.apiSap.getStyles())

    def getSapModels(self):
        try:
            return self.apiSap.getModels()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def openManagementModels(self):
        managementModels = ManagementModelsSingleton.getInstance(self)
        if managementModels.isVisible():
            managementModels.toTopLevel()
            return
        self.loadManagementDialogData(managementModels, self.getSapModels())
        managementModels.show()

    def addModel(self):
        managementModels = ManagementModelsSingleton.getInstance(self)
        addModelForm = AddModelFormSingleton.getInstance(parent=managementModels)
        if not addModelForm.exec():
            return
        inputModelData = addModelForm.getData()
        managementModels.addRow(
            inputModelData['modelName'],
            inputModelData['modelDescription'],
            inputModelData['modelXml']
        )

    def updateSapModels(self, modelsData):
        managementModels = ManagementModelsSingleton.getInstance(self)
        try:
            message = self.apiSap.updateModels(modelsData)
            managementModels.showInfo('Aviso', message)
        except Exception as e:
            managementModels.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementModels, self.getSapModels())

    #interface
    def getSapRules(self):
        try:
            return self.apiSap.getRules()
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
            return []

    def openManagementRules(self):
        managementRules = ManagementRulesSingleton.getInstance(self)
        if managementRules.isVisible():
            managementRules.toTopLevel()
            return
        managementRules.setGroupData(self.getSapRules()['grupo_regras'])
        rulesData = self.getSapRules()['regras']
        for ruleData in rulesData:
            ruleData['qgisExpressionWidget'] = self.getQgisWidgetExpression()
        self.loadManagementDialogData(managementRules, rulesData)
        managementRules.show()

    def getQgisWidgetExpression(self):
        return self.gisPlatform.getWidgetExpression()
        
    def openManagementRuleSet(self, groupData):
        managementRules = ManagementRulesSingleton.getInstance(self)
        managementRuleSet = ManagementRuleSetSingleton.getInstance(self, managementRules)
        self.loadManagementDialogData(managementRuleSet, groupData)
        if not managementRuleSet.exec():
            return
        managementRules.setGroupData(
            managementRuleSet.getAllTableData()
        )
        
    def addRules(self, groupList):
        managementRules = ManagementRulesSingleton.getInstance(self)
        addRuleForm = AddRuleFormSingleton.getInstance(
            self.gisPlatform.getWidgetExpression(),
            parent=managementRules
        )
        addRuleForm.setGroupList(groupList)
        if not addRuleForm.exec():
            return
        inputRuleData = addRuleForm.getData()
        managementRules.addRow(
            '', 
            inputRuleData['grupo_regra'], 
            inputRuleData['schema'], 
            inputRuleData['camada'],
            inputRuleData['atributo'],
            inputRuleData['regra'], 
            inputRuleData['descricao'],
            self.gisPlatform.getWidgetExpression()
        )

    def addRuleSet(self, groupList):
        managementRules = ManagementRulesSingleton.getInstance(self)
        managementRuleSet = ManagementRuleSetSingleton.getInstance(self, managementRules)
        addRuleSetForm = AddRuleSetFormSingleton.getInstance(
            parent=managementRuleSet
        )
        addRuleSetForm.setCurrentGroups(groupList)
        if not addRuleSetForm.exec():
            return
        inputRuleSetData = addRuleSetForm.getData()
        managementRuleSet.addRow(inputRuleSetData['grupo_regra'], inputRuleSetData['cor_rgb'], '0')

    def importRulesCsv(self):
        managementRules = ManagementRulesSingleton.getInstance(self)
        addRulesCsvForm = AddRulesCsvFormSingleton.getInstance(sapCtrl=self, parent=managementRules)
        if not addRulesCsvForm.exec():
            return
        currentGroupRules = [ d['grupo_regra'].lower() for d in managementRules.getGroupData()]
        rules = RulesSingleton.getInstance()
        newRules = rules.getRulesFromCsv(addRulesCsvForm.getData()['pathRulesCsv'])
        for groupRule in newRules:
            if not ( groupRule.lower() in currentGroupRules):
                groupData = managementRules.getGroupData()
                groupData.append({
                    'grupo_regra' : groupRule,
                    'cor_rgb' : newRules[groupRule]['cor_rgb']
                })
                managementRules.setGroupData(groupData)
            for ruleData in newRules[groupRule]['regras']:
                managementRules.addRow(
                    '', 
                    groupRule, 
                    ruleData['schema'], 
                    ruleData['camada'],
                    ruleData['atributo'], 
                    ruleData['regra'], 
                    ruleData['descricao'],
                    self.getQgisWidgetExpression()
                )
        managementRules.showInfo('Aviso', 'Regras carregadas!')

    def downloadCsvRulesTemplate(self, destPath):
        rules = RulesSingleton.getInstance()
        rules.saveTemplateCsv(destPath)

    def updateSapRules(self, rulesData, groupsData):
        managementRules = ManagementRulesSingleton.getInstance(self)
        try:
            message = self.apiSap.updateRules(rulesData, groupsData)
            managementRules.showInfo('Aviso', message)
        except Exception as e:
            managementRules.showError('Aviso', str(e))
        finally:
            rulesData = self.getSapRules()['regras']
            for ruleData in rulesData:
                ruleData['qgisExpressionWidget'] = self.getQgisWidgetExpression()
            self.loadManagementDialogData(managementRules, rulesData)

    def downloadQgisProject(self, destPath):
        try:
            projectXml = self.apiSap.getQgisProject()
            with open(destPath, 'w') as f:
                f.write(projectXml)
            self.dockSap.showInfo('Aviso', 'Projeto criado com sucesso!')
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def loadLayersQgisProject(self, projectInProgress):
        try:
            layersData = self.apiSap.getLayersQgisProject(projectInProgress)
            print(layersData)
            dbName = layersData['banco_dados']['nome_db']
            dbHost = layersData['banco_dados']['servidor']
            dbPort = layersData['banco_dados']['porta']
            dbUser = layersData['banco_dados']['login']
            dbPassword = layersData['banco_dados']['senha']
            groupBase = self.gisPlatform.addLayerGroup('Acompanhamento')
            groupProduction = self.gisPlatform.addLayerGroup('Linha de produção', groupBase)
            groupPhase = self.gisPlatform.addLayerGroup('Fase', groupBase)
            groupSubPhase = self.gisPlatform.addLayerGroup('Subfase', groupBase)
            for viewData in layersData['views']:
                """ if viewData['tipo'] == 'fase':
                    groupParent = groupPhase
                elif viewData['tipo'] == 'subfase':
                    groupParent = groupSubPhase
                else:
                    groupParent = groupProduction
                groupProject = self.gisPlatform.addLayerGroup(viewData['projeto'], groupParent) """
                self.gisPlatform.loadLayer(
                    dbName, 
                    dbHost, 
                    dbPort, 
                    dbUser, 
                    dbPassword, 
                    viewData['schema'], 
                    viewData['nome'], 
                    #groupProject
                )
                print('a')
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def synchronizeUserInformation(self):
        try:
            message = self.apiSap.synchronizeUserInformation()
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def activeRemoveByClip(self):
        self.gisPlatform.activeMapToolByToolName('removeByClip')

    def activeRemoveByIntersect(self):
        self.gisPlatform.activeMapToolByToolName('removeByIntersect')

    def getUsersFromAuthService(self):
        try:
            users = self.apiSap.getUsersFromAuthService()
            return users
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def importUsersAuthService(self, usersIds):
        try:
            message = self.apiSap.importUsersAuthService(usersIds)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def openManagementUsersPrivileges(self):
        managementUsersPrivileges = ManagementUsersPrivilegesSingleton.getInstance(self)
        if managementUsersPrivileges.isVisible():
            managementUsersPrivileges.toTopLevel()
            return
        self.loadManagementDialogData(managementUsersPrivileges, self.getSapUsers())
        managementUsersPrivileges.show()

    def updateUsersPrivileges(self, usersData):
        managementUsersPrivileges = ManagementUsersPrivilegesSingleton.getInstance(self)
        try:
            message = self.apiSap.updateUsersPrivileges(usersData)
            managementUsersPrivileges.showInfo('Aviso', message)
        except Exception as e:
            managementUsersPrivileges.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementUsersPrivileges, self.getSapUsers())

    #interface
    def deleteActivities(self, activityIds):
        try:
            message = self.apiSap.deleteActivities(
                activityIds
            )
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def createActivities(self, workspacesIds, stepId):
        try:
            message = self.apiSap.createActivities(workspacesIds, stepId )
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def resetPrivileges(self):
        try:
            message = self.apiSap.resetPrivileges()
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def getSapDatabase(self):
        return self.apiSap.getDatabases()
    
    def openManagementImportLayers(self):
        managementImportLayers = ManagementImportLayersSingleton.getInstance(self)
        if managementImportLayers.isVisible():
            managementImportLayers.toTopLevel()
            return
        managementImportLayers.show()

    def loadManagementImportLayers(self, dbHost, dbPort, dbName):
        managementImportLayers = ManagementImportLayersSingleton.getInstance(self)
        postgresLayers = self.getLayersFromPostgres(dbHost, dbPort, dbName)
        layersRows = []
        sapLayers = self.getSapLayers()
        sapLayersNames = [ d['nome'] for d in sapLayers ]
        for layerData in postgresLayers:
            if layerData['nome'] in sapLayersNames:
                continue
            layersRows.append({
                'nome' : layerData['nome'],
                'schema' : layerData['schema'],
                'alias' : '',
                'documentacao' : ''
                
            })
        self.loadManagementDialogData(managementImportLayers, layersRows)

    def importLayers(self, layersImported):
        managementImportLayers = ManagementImportLayersSingleton.getInstance(self)
        try:
            message = self.apiSap.importLayers(layersImported)
            managementImportLayers.showInfo('Aviso', message)
        except Exception as e:
            managementImportLayers.showError('Aviso', str(e))
        finally:
            dbName = managementImportLayers.getCurrentDatabase()
            dbData = managementImportLayers.getDatabaseData(dbName)
            if not ( dbData is None ):
                self.loadManagementImportLayers(
                    dbData['servidor'],
                    dbData['porta'],
                    dbData['nome']
                )
        
    def getSapLayers(self):
        return self.apiSap.getLayers()

    def getLayersFromPostgres(self, dbHost, dbPort, dbName):
        managementImportLayers = ManagementImportLayersSingleton.getInstance(self)
        try:
            postgres = DatabasesFactoryMethod.getDatabase('postgres')
            auth = self.apiSap.getAuthDatabase()
            postgres.setConnection(dbName, dbHost, dbPort, auth['login'], auth['senha'])
            return postgres.getLayers()
        except:
            managementImportLayers.showError('Aviso', 'Banco de dados não acessível!')
        return []

    def openManagementEditLayers(self):
        managementEditLayers = ManagementEditLayersSingleton.getInstance(self)
        if managementEditLayers.isVisible():
            managementEditLayers.toTopLevel()
            return
        self.loadManagementDialogData(managementEditLayers, self.getSapLayers())
        managementEditLayers.show()

    def updateLayers(self, layersData):
        managementEditLayers = ManagementEditLayersSingleton.getInstance(self)
        try:
            message = self.apiSap.updateLayers(layersData)
            managementEditLayers.showInfo('Aviso', message)
        except Exception as e:
            managementEditLayers.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementEditLayers, self.getSapLayers())

    def deleteLayers(self, deletedLayersIds):
        managementEditLayers = ManagementEditLayersSingleton.getInstance(self)
        try:
            message = self.apiSap.deleteLayers(deletedLayersIds)
            managementEditLayers.showInfo('Aviso', message)
        except Exception as e:
            managementEditLayers.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementEditLayers, self.getSapLayers())

    def getSapLots(self):
       return self.apiSap.getLots()

    def alterLot(self, workspacesIds, lotId):
        try:
            message = self.apiSap.alterLot(workspacesIds, lotId)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def revokePrivileges(self, dbHost, dbPort, dbName):
        try:
            message = self.apiSap.revokePrivileges(dbHost, dbPort, dbName)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
    
    def getSapMenus(self):
        return self.apiSap.getMenus()

    def copySapSettingsToLocalMode(self,
            dbHost,
            dbPort,
            dbName,
            copyStyles,
            copyModels,
            copyRules,
            copyMenus
        ):
        try:
            postgres = DatabasesFactoryMethod.getDatabase('postgres')
            auth = self.apiSap.getAuthDatabase()
            postgres.setConnection(dbName, dbHost, dbPort, auth['login'], auth['senha'])
            if copyStyles:
                postgres.insertStyles(self.getSapStyles())
            if copyModels:
                postgres.insertModels(self.getSapModels())
            if copyRules:
                postgres.insertRules(self.getSapRules()['regras'])
            if copyMenus:
                postgres.insertMenus(self.getSapMenus())
            self.dockSap.showInfo('Aviso', """Dados copiados!""")
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def openManagementFmeServers(self):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        if managementFmeServers.isVisible():
            managementFmeServers.toTopLevel()
            return
        self.loadManagementDialogData(managementFmeServers, self.apiSap.getFmeServers())
        managementFmeServers.show()

    def addFmeServer(self):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        addFmeServerForm = AddFmeServerFormSingleton.getInstance(parent=managementFmeServers)
        if not addFmeServerForm.exec():
            return
        inputFmeServerData = addFmeServerForm.getData()
        self.createFmeServers([inputFmeServerData])

    def createFmeServers(self, fmeServers):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        try:
            message = self.apiSap.createFmeServers(fmeServers)
            managementFmeServers.showInfo('Aviso', message)
        except Exception as e:
            managementFmeServers.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementFmeServers, self.apiSap.getFmeServers())

    def deleteFmeServers(self, fmeServersIds):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        try:
            message = self.apiSap.deleteFmeServers(fmeServersIds)
            managementFmeServers.showInfo('Aviso', message)
        except Exception as e:
            managementFmeServers.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementFmeServers, self.apiSap.getFmeServers())

    def updateFmeServers(self, fmeServers):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        try:
            message = self.apiSap.updateFmeServers(fmeServers)
            managementFmeServers.showInfo('Aviso', message)
        except Exception as e:
            managementFmeServers.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementFmeServers, self.apiSap.getFmeServers())

    def openManagementFmeProfiles(self):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        if managementFmeProfiles.isVisible():
            managementFmeProfiles.toTopLevel()
            return
        self.loadManagementDialogData(managementFmeProfiles, self.apiSap.getFmeProfiles())
        managementFmeProfiles.show()

    def loadManagementDialogData(self, managementDialog, rowsData):
        managementDialog.clearAllItems()
        managementDialog.addRows(rowsData)
        managementDialog.adjustColumns()

    def getFmeRoutines(self, server, port):
        return self.fmeCtrl.getRoutines(server, port)

    def addFmeProfile(self):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        addFmeProfileForm = AddFmeProfileFormSingleton.getInstance(parent=managementFmeProfiles, sapCtrl=self)
        addFmeProfileForm.loadFmeServers(self.apiSap.getFmeServers())
        addFmeProfileForm.loadSubphases(self.apiSap.getSubphases())
        if not addFmeProfileForm.exec():
            return
        inputFmeProfileData = addFmeProfileForm.getData()
        self.createFmeProfiles([inputFmeProfileData])

    def createFmeProfiles(self, fmeProfiles):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        try:
            message = self.apiSap.createFmeProfiles(fmeProfiles)
            managementFmeProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementFmeProfiles.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementFmeProfiles, self.apiSap.getFmeProfiles())

    def deleteFmeProfiles(self, fmeProfilesIds):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        try:
            message = self.apiSap.deleteFmeProfiles(fmeProfilesIds)
            managementFmeProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementFmeProfiles.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementFmeProfiles, self.apiSap.getFmeProfiles())

    def updateFmeProfiles(self, fmeProfiles):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        try:
            message = self.apiSap.updateFmeProfiles(fmeProfiles)
            managementFmeProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementFmeProfiles.showError('Aviso', str(e))
        finally:
            self.loadManagementDialogData(managementFmeProfiles, self.apiSap.getFmeProfiles())

    def getSapStepsByFeatureId(self, featureId):
        def sortByOrder(elem):
            return elem['ordem']
        def sortByName(elem):
            return elem['nome']
        subphaseId = self.gisPlatform.getActiveLayerAttribute(featureId, 'subfase_id')
        filteredSteps = [ s for s in self.apiSap.getSteps() if s['subfase_id'] == subphaseId]
        filteredSteps.sort(key=sortByOrder)
        stepsNames = []
        for step in filteredSteps:
            if step['nome'] in stepsNames:
                number = stepsNames.count(step['nome']) + 1
            else:
                stepsNames.append(step['nome'])
                number = 1
            step['nome'] = "{0} {1}".format(step['nome'], number)
        filteredSteps.sort(key=sortByName)
        return filteredSteps