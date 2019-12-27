from Ferramentas_Gerencia.sap.controllers.interface.ISapCtrl import ISapCtrl

from Ferramentas_Gerencia.sap.models.api.singleton.apiSapSingleton import ApiSapSingleton
from Ferramentas_Gerencia.sap.models.functionsSettings.singleton.functionsSettingsSingleton import FunctionsSettingsSingleton

from Ferramentas_Gerencia.sap.views.dock.builder.managementDockBuilder import ManagementDockBuilder
from Ferramentas_Gerencia.sap.views.dock.director.dockDirector import DockDirector
from Ferramentas_Gerencia.sap.views.dialogs.singleton.loginSingleton import LoginSingleton
from Ferramentas_Gerencia.sap.views.dialogs.singleton.managementStylesSingleton  import ManagementStylesSingleton
from Ferramentas_Gerencia.sap.views.dialogs.singleton.managementModelsSingleton  import ManagementModelsSingleton
from Ferramentas_Gerencia.sap.views.dialogs.singleton.managementRulesSingleton  import ManagementRulesSingleton
from Ferramentas_Gerencia.sap.views.dialogs.singleton.addStyleFormSingleton  import AddStyleFormSingleton
from Ferramentas_Gerencia.sap.views.dialogs.singleton.addModelFormSingleton  import AddModelFormSingleton
from Ferramentas_Gerencia.sap.views.dialogs.singleton.addRuleFormSingleton  import AddRuleFormSingleton

class SapManagerCtrl(ISapCtrl):

    def __init__(self, gisPlatform):
        super(SapManagerCtrl, self).__init__(gisPlatform)
        self.loginView = LoginSingleton.getInstance(loginCtrl=self)
        self.apiSap = ApiSapSingleton.getInstance()
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
        try:
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
            self.loginView.showErroMessage('Aviso', str(e))

    #interface
    def getSapUsers(self):
        try:
            return self.apiSap.getSapUsers()
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
            return []

    #interface
    def getSapProfiles(self):
        try:
            return self.apiSap.getSapProfiles()
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
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
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

    #interface
    def addNewRevisionCorrection(self, activityIds):
        try:
            message = self.apiSap.addNewRevisionCorrection(
                activityIds
            )
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

    #interface
    def advanceActivityToNextStep(self, activityIds, endStep):
        try:
            message = self.apiSap.advanceActivityToNextStep(
                activityIds, 
                endStep
            )
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

    def createWorkUnit(self, inputData):
        try:
            #classx.run(asf)
            message = self.apiSap.createWorkUnit(
                inputData
            )
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

    #interface
    def createPriorityGroupActivity(self, activityIds, priority, profileId):
        try:
            message = self.apiSap.createPriorityGroupActivity(
                activityIds, 
                priority, 
                profileId
            )
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

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
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
    
    #interface
    def lockWorkspace(self, workspacesIds):
        try:
            message = self.apiSap.lockWorkspace(workspacesIds)
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

    def openActivity(self, activityIds):
        try:
            message = self.apiSap.openActivity(activityIds)
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

    #interface
    def openNextActivityByUser(self, userId):
        try:
            message = self.apiSap.openNextActivityByUser(userId)
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

    #interface
    def pauseActivity(self, workspacesIds):
        try:
            message = self.apiSap.pauseActivity(workspacesIds)
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
    
    #interface
    def restartActivity(self, workspacesIds):
        try:
            message = self.apiSap.restartActivity(workspacesIds)
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
    
    #interface
    def returnActivityToPreviousStep(self, activityIds, preserveUser):
        try:
            message = self.apiSap.returnActivityToPreviousStep(activityIds, preserveUser)
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

    #interface
    def setPriorityActivity(self, activityIds, priority, userId):
        try:
            message = self.apiSap.setPriorityActivity(activityIds, priority, userId)
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

     #interface
    def unlockWorkspace(self, workspacesIds):
        try:
            message = self.apiSap.unlockWorkspace(workspacesIds)
            self.dockSap.showMessageInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))

    #interface
    def getSapStyles(self):
        try:
            return self.apiSap.getSapStyles()
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
            return []

    def openManagementStyles(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
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
        managementStyles.show()
        
    def loadStylesFromLayersSelection(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        stylesData = self.gisPlatform.getQmlStyleFromLayersTreeSelection()
        if len(stylesData) == 0:
            managementStyles.showMessageErro('Aviso', "Selecione no mínimo uma camada.")
            return
        addStyleForm = AddStyleFormSingleton.getInstance(parent=managementStyles)
        accepted = addStyleForm.exec()
        if accepted:
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
            managementStyles.showMessageInfo('Aviso', message)
        except Exception as e:
            managementStyles.showMessageErro('Aviso', str(e))

    def getSapModels(self):
        try:
            return self.apiSap.getSapModels()
        except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
            return []

    def openManagementModels(self):
        managementModels = ManagementModelsSingleton.getInstance(self)
        for modelData in self.getSapModels():
            managementModels.addRow(
                modelData['nome'],
                modelData['descricao'],
                modelData['model_xml']
            )
        managementModels.show()

    def addModel(self):
        managementModels = ManagementModelsSingleton.getInstance(self)
        addModelForm = AddModelFormSingleton.getInstance(parent=managementModels)
        accepted = addModelForm.exec()
        if accepted:
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
            managementModels.showMessageInfo('Aviso', message)
        except Exception as e:
            managementModels.showMessageErro('Aviso', str(e))

    #interface
    def getSapRules(self):
        #try:
        return self.apiSap.getSapRules()
        """ except Exception as e:
            self.dockSap.showMessageErro('Aviso', str(e))
            return [] """


    def openManagementRules(self):
        managementRules = ManagementRulesSingleton.getInstance(self)
        managementRules.setGroupColorData(self.getSapRules()['grupo_regras'])
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
        managementRules.show()

    def editColorRules(self):
        pass

    def addRules(self):
        managementRules = ManagementRulesSingleton.getInstance(self)
        addRuleForm = AddRuleFormSingleton.getInstance(
            self.gisPlatform.getWidgetExpression(),
            parent=managementRules
        )
        accepted = addRuleForm.exec()
        if accepted:
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

    def saveRulesSap(self, rulesData, groupsData):
        managementRules = ManagementRulesSingleton.getInstance(self)
        try:
            message = self.apiSap.setSapRules(rulesData, groupsData)
            managementRules.showMessageInfo('Aviso', message)
        except Exception as e:
            managementRules.showMessageErro('Aviso', str(e))