import os

from Ferramentas_Gerencia.sap.interfaces.ISapCtrl import ISapCtrl

from Ferramentas_Gerencia.sap.factory.sapApiSingleton import SapApiSingleton
from Ferramentas_Gerencia.sap.factory.functionsSettingsSingleton import FunctionsSettingsSingleton
from Ferramentas_Gerencia.sap.factory.managementDockBuilder import ManagementDockBuilder
from Ferramentas_Gerencia.sap.factory.dockDirector import DockDirector
from Ferramentas_Gerencia.sap.factory.loginSingleton import LoginSingleton
from Ferramentas_Gerencia.sap.factory.managementStylesSingleton  import ManagementStylesSingleton
from Ferramentas_Gerencia.sap.factory.managementModelsSingleton  import ManagementModelsSingleton
from Ferramentas_Gerencia.sap.factory.managementRulesSingleton  import ManagementRulesSingleton
from Ferramentas_Gerencia.sap.factory.managementRuleSetSingleton  import ManagementRuleSetSingleton
from Ferramentas_Gerencia.sap.factory.managementUsersPrivilegesSingleton  import ManagementUsersPrivilegesSingleton
from Ferramentas_Gerencia.sap.factory.addStyleFormSingleton  import AddStyleFormSingleton
from Ferramentas_Gerencia.sap.factory.addModelFormSingleton  import AddModelFormSingleton
from Ferramentas_Gerencia.sap.factory.addRuleFormSingleton  import AddRuleFormSingleton
from Ferramentas_Gerencia.sap.factory.addRuleSetFormSingleton  import AddRuleSetFormSingleton
from Ferramentas_Gerencia.sap.factory.addRulesCsvFormSingleton  import AddRulesCsvFormSingleton
from Ferramentas_Gerencia.sap.factory.rulesSingleton  import RulesSingleton

class SapManagerCtrl(ISapCtrl):

    def __init__(self, gisPlatform):
        super(SapManagerCtrl, self).__init__(gisPlatform)
        self.loginView = LoginSingleton.getInstance(loginCtrl=self)
        self.apiSap = SapApiSingleton.getInstance()
        self.dockSap = None

    def loadDockSap(self):
        dockDirector = DockDirector()
        managementDockBuilder = ManagementDockBuilder()
        dockDirector.constructSapManagementDock(managementDockBuilder, sapCtrl=self)
        self.dockSap = managementDockBuilder.getResult()
        self.gisPlatform.addDockWidget(self.dockSap)

    def loadLoginView(self):
        self.loginView.loadData(
            user=self.gisPlatform.getSettingsVariable('sapmanager:user'), 
            server=self.gisPlatform.getSettingsVariable('sapmanager:server')
        )
        
    def saveLoginData(self, user, server):
        self.gisPlatform.setSettingsVariable('sapmanager:user', user)
        self.gisPlatform.setSettingsVariable('sapmanager:server', server)

    #interface
    def authUser(self, user, password, server):
        self.saveLoginData(user, server)
        self.apiSap.setServer(server)
        #try:
        response = self.apiSap.loginAdminUser(
            user, 
            password,
            self.gisPlatform.getVersion(),
            self.gisPlatform.getPluginsVersions()
        )
        self.apiSap.setToken(response['dados']['token'])
        self.loadDockSap()
        self.loginView.closeView()
        """ except Exception as e:
            self.loginView.showError('Aviso', str(e)) """

    #interface
    def getSapUsers(self):
        try:
            return self.apiSap.getSapUsers()
        except Exception as e:
            self.loginView.showError('Aviso', str(e))
            return []

    #interface
    def getSapProfiles(self):
        try:
            return self.apiSap.getSapProfiles()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def getValuesFromLayer(self, functionName, fieldName):
        functionSettings = FunctionsSettingsSingleton.getInstance()
        fieldSettings = functionSettings.getSettings(functionName, fieldName)
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

    #interface
    def showLoginView(self):
        self.loadLoginView()
        self.loginView.showView()

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

    def createWorkUnit(self, inputData):
        try:
            #classx.run(asf)
            message = self.apiSap.createWorkUnit(
                inputData
            )
            self.dockSap.showInfo('Aviso', message)
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
    def fillCommentActivity(self, activityIds, commentActivity, commentWorkspace, commentStep, commentSubfase):
        try:
            message = self.apiSap.fillCommentActivity(
                activityIds, 
                commentActivity, 
                commentWorkspace, 
                commentStep, 
                commentSubfase
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
            message = self.apiSap.openActivity(activityIds)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    #interface
    def openNextActivityByUser(self, userId, nextActivity):
        try:
            message = self.apiSap.openNextActivityByUser(userId, nextActivity)
            self.dockSap.showInfo('Aviso', message)
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
            return self.apiSap.getSapStyles()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def openManagementStyles(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        if managementStyles.isVisible():
            managementStyles.toTopLevel()
            return
        self.loadManagementStyles()
        managementStyles.show()

    def loadManagementStyles(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        managementStyles.clearAllItems()
        for styleData in self.apiSap.getSapStyles():
            managementStyles.addRow(
                styleData['f_table_schema'],
                styleData['f_table_name'],
                styleData['stylename'],
                styleData['styleqml'],
                styleData['stylesld'],
                styleData['ui'],
                styleData['f_geometry_column']
            )
        managementStyles.adjustColumns()
        
    def loadStylesFromLayersSelection(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        stylesData = self.gisPlatform.getQmlStyleFromLayersTreeSelection()
        if len(stylesData) == 0:
            managementStyles.showError('Aviso', "Selecione no mínimo uma camada.")
            return
        addStyleForm = AddStyleFormSingleton.getInstance(parent=managementStyles)
        if not addStyleForm.exec():
            return
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

    def saveStylesSap(self, stylesData):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        try:
            message = self.apiSap.setSapStyles(stylesData)
            self.loadManagementStyles()
            managementStyles.showInfo('Aviso', message)
        except Exception as e:
            managementStyles.showError('Aviso', str(e))

    def getSapModels(self):
        try:
            return self.apiSap.getSapModels()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def openManagementModels(self):
        managementModels = ManagementModelsSingleton.getInstance(self)
        if managementModels.isVisible():
            managementModels.toTopLevel()
            return
        self.loadManagementModels()
        managementModels.show()

    def loadManagementModels(self):
        managementModels = ManagementModelsSingleton.getInstance(self) 
        managementModels.clearAllItems()
        for modelData in self.getSapModels():
            managementModels.addRow(
                modelData['nome'],
                modelData['descricao'],
                modelData['model_xml']
            )
        managementModels.adjustColumns()

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

    def saveModelsSap(self, modelsData):
        managementModels = ManagementModelsSingleton.getInstance(self)
        try:
            message = self.apiSap.setSapModels(modelsData)
            self.loadManagementModels()
            managementModels.showInfo('Aviso', message)
        except Exception as e:
            managementModels.showError('Aviso', str(e))

    #interface
    def getSapRules(self):
        try:
            return self.apiSap.getSapRules()
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
            return []

    def openManagementRules(self):
        managementRules = ManagementRulesSingleton.getInstance(self)
        if managementRules.isVisible():
            managementRules.toTopLevel()
            return
        self.loadManagementRules()
        managementRules.show()

    def loadManagementRules(self):
        managementRules = ManagementRulesSingleton.getInstance(self)
        managementRules.setGroupData(self.getSapRules()['grupo_regras'])
        managementRules.clearAllItems()
        for ruleData in self.getSapRules()['regras']:  
            managementRules.addRow(
                str(ruleData['id']), 
                ruleData['grupo_regra'], 
                ruleData['schema'], 
                ruleData['camada'],
                ruleData['atributo'], 
                ruleData['regra'], 
                ruleData['descricao'],
                self.gisPlatform.getWidgetExpression()
            )
        managementRules.adjustColumns()
        
    def openManagementRuleSet(self, groupData):
        managementRules = ManagementRulesSingleton.getInstance(self)
        managementRuleSet = ManagementRuleSetSingleton.getInstance(self, managementRules)
        managementRuleSet.clearAllItems()
        for group in groupData:  
            managementRuleSet.addRow(group['grupo_regra'], group['cor_rgb'], str(group['count']))
        managementRuleSet.adjustColumns()
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
        addRulesCsvForm = AddRulesCsvFormSingleton.getInstance(
            sapCtrl=self,
            parent=managementRules
        )
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
                    self.gisPlatform.getWidgetExpression()
                )
        managementRules.showInfo('Aviso', 'Regras carregadas!')

    def downloadCsvRulesTemplate(self, destPath):
        rules = RulesSingleton.getInstance()
        rules.saveTemplateCsv(destPath)

    def saveRulesSap(self, rulesData, groupsData):
        managementRules = ManagementRulesSingleton.getInstance(self)
        try:
            message = self.apiSap.setSapRules(rulesData, groupsData)
            self.loadManagementRules()
            managementRules.showInfo('Aviso', message)
        except Exception as e:
            managementRules.showError('Aviso', str(e))

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
            layers = self.apiSap.getLayersQgisProject(projectInProgress)
            print(layers)
            #self.dockSap.showInfo('Aviso', 'Projeto criado com sucesso!')
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
        self.loadManagementUsersPrivileges()
        managementUsersPrivileges.show()

    def loadManagementUsersPrivileges(self):
        managementUsersPrivileges = ManagementUsersPrivilegesSingleton.getInstance(self)
        managementUsersPrivileges.clearAllItems()
        for userData in self.getSapUsers():  
            managementUsersPrivileges.addRow(
                userData['uuid'], 
                userData['nome_guerra'], 
                userData['administrador'], 
                userData['ativo']
            )
        managementUsersPrivileges.adjustColumns()

    def saveUsersPrivileges(self, usersData):
        managementUsersPrivileges = ManagementUsersPrivilegesSingleton.getInstance(self)
        try:
            message = self.apiSap.setUsersPrivileges(usersData)
            self.loadManagementUsersPrivileges()
            managementUsersPrivileges.showInfo('Aviso', message)
        except Exception as e:
            managementUsersPrivileges.showError('Aviso', str(e))

    #interface
    def deleteActivities(self, layersIds):
        try:
            message = self.apiSap.deleteActivities(
                layersIds
            )
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
