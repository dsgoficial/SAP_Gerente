from PyQt5.QtCore import QObject
from Ferramentas_Gerencia.interfaces.IManagementToolCtrl import IManagementToolCtrl
from Ferramentas_Gerencia.factories.functionsSettingsSingleton import FunctionsSettingsSingleton
from Ferramentas_Gerencia.factories.widgetFactory import WidgetFactory
from Ferramentas_Gerencia.modules.databases.factories.databasesFactory  import DatabasesFactory
from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory
import sip
import os
import re

class ManagementToolCtrl(QObject, IManagementToolCtrl):

    def __init__(self, 
            qgis, 
            fmeCtrl, 
            sapCtrl,
            databasesFactory=DatabasesFactory(),
            functionsSettings=FunctionsSettingsSingleton.getInstance(),
            messageFactory=UtilsFactory().createMessageFactory(),
            widgetFactory=WidgetFactory()
        ):
        super(ManagementToolCtrl, self).__init__()
        self.qgis = qgis
        self.fmeCtrl = fmeCtrl
        self.databasesFactory = databasesFactory
        self.messageFactory = messageFactory
        self.widgetFactory = widgetFactory
        self.functionsSettings = functionsSettings
        self.sapCtrl = sapCtrl
        self.dockSap = None
        self.assocUserToProjDlg = None
        self.assocUserToProfDlg = None
        self.addProjDlg = None
        self.addProfProdDlg = None
        self.userProfManDlg = None
        self.aProfProdRelDlg = None
        self.cProfProdDlg = None
        self.userProfEditDlg = None
        self.menuBarActions = []
        self.createActionsMenuBar()
        self.createMenuBar() 

    def showErrorMessageBox(self, parent, title, message):
        parent = self.qgis.getMainWindow() if not parent else parent
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(parent, title, message)

    def showQuestionMessageBox(self, parent, title, message):
        parent = self.qgis.getMainWindow() if not parent else parent
        questionMessageBox = self.messageFactory.createMessage('QuestionMessageBox')
        return questionMessageBox.show(parent, title, message)
    
    def showInfoMessageBox(self, parent, title, message):
        parent = self.qgis.getMainWindow() if not parent else parent
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(parent, title, message)       

    def createMenuBar(self):
        self.menuBarMain = self.qgis.addMenuBar('Ferramentas de Gerência')
        for action in self.getMenuBarActions():
            self.menuBarMain.addAction(action)
        self.menuBarMain.setDisabled(True)

    def createActionsMenuBar(self):
        menuBarActions = []
        for actionConfig in self.getMenuBarActionSettings():
            action = self.qgis.createAction(
                actionConfig['name'],
                actionConfig['iconPath'],
                actionConfig['callback'],
                actionConfig['shortcut']
            )
            menuBarActions.append(action)
        self.setMenuBarActions(menuBarActions)

    def setMenuBarActions(self, menuBarActions):
        self.menuBarActions = menuBarActions

    def getMenuBarActions(self):
        return self.menuBarActions

    def getMenuBarActionSettings(self):
        return []

    def loadDockSap(self):
        self.dockSap = self.widgetFactory.create('DockSap', self)
        self.qgis.addDockWidget(self.dockSap)
        self.disableMenuBar(False)

    def disableMenuBar(self, b):
        self.menuBarMain.setDisabled(b)

    def getValuesFromLayer(self, functionName, fieldName):
        fieldSettings = self.functionsSettings.getSettings(functionName, fieldName)
        try:
            for layerOptions in fieldSettings:
                values = self.qgis.getFieldValuesFromLayer(
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

    def createWorkUnit(self, layerName, size, overlay, deplace, prefixName, onlySelected):
        try:
            self.qgis.generateWorkUnit(
                layerName, size, overlay, deplace, prefixName, onlySelected
            )
            self.showInfoMessageBox(self.dockSap, 'Aviso', 'Unidades de trabalho geradas com sucesso!')
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def openManagementStyles(self):
        managementStyles = self.widgetFactory.create('ManagementStyles', self)
        if managementStyles.isVisible():
            managementStyles.toTopLevel()
            return
        managementStyles.addRows( self.getSapStyles(parent=managementStyles) )
        managementStyles.show()

    def getSapStyles(self, parent=None):
        try:
            return self.sapCtrl.getStyles()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []
        
    def loadStylesFromLayersSelection(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        stylesData = self.qgis.getQmlStyleFromLayersTreeSelection()
        if len(stylesData) == 0:
            managementStyles.showError('Aviso', "Selecione no mínimo uma camada.")
            return
        addStyleForm = self.widgetFactory.create('AddStyleForm', managementStyles)
        if not addStyleForm.exec():
            return
        stylesRows = []
        for style in stylesData:
            style['stylename'] = addStyleForm.getData()['styleName']
        self.createSapStyles(stylesData)
       
    def applyStylesOnLayers(self, stylesData):
        self.qgis.applyStylesOnLayers(stylesData)

    def createSapStyles(self, data):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        try:
            message = self.sapCtrl.createStyles(data)
            self.showInfoMessageBox(managementStyles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementStyles, 'Aviso', str(e))
        managementStyles.addRows( self.sapCtrl.getStyles() )

    def updateSapStyles(self, data):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        try:
            message = self.sapCtrl.updateStyles(data)
            self.showInfoMessageBox(managementStyles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementStyles, 'Aviso', str(e))
        managementStyles.addRows( self.sapCtrl.getStyles() )

    def deleteSapStyles(self, data):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        try:
            message = self.sapCtrl.deleteStyles(data)
            self.showInfoMessageBox(managementStyles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementStyles, 'Aviso', str(e))
        managementStyles.addRows( self.sapCtrl.getStyles() )

    def getSapModels(self):
        try:
            return self.sapCtrl.getModels()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def openManagementModels(self):
        managementModels = self.widgetFactory.create('ManagementModels', self)
        if managementModels.isVisible():
            managementModels.toTopLevel()
            return
        managementModels.addRows(self.getSapModels())
        managementModels.show()

    def addModel(self):
        managementModels = self.widgetFactory.create('ManagementModels', self)
        addModelForm = self.widgetFactory.create('AddModelForm', managementModels)
        if not addModelForm.exec():
            return
        inputModelData = addModelForm.getData()
        self.createSapModels([inputModelData])

    def createSapModels(self, data):
        managementModels = self.widgetFactory.create('ManagementModels', self)
        try:
            message = self.sapCtrl.createModels(data)
            managementModels.showInfo('Aviso', message)
        except Exception as e:
            managementModels.showError('Aviso', str(e))
        finally:
            managementModels.addRows(self.getSapModels())

    def updateSapModels(self, data):
        managementModels = self.widgetFactory.create('ManagementModels', self)
        try:
            message = self.sapCtrl.updateModels(data)
            managementModels.showInfo('Aviso', message)
        except Exception as e:
            managementModels.showError('Aviso', str(e))
        finally:
            managementModels.addRows(self.getSapModels())

    def deleteSapModels(self, ids):
        managementModels = self.widgetFactory.create('ManagementModels', self)
        try:
            message = self.sapCtrl.deleteModels(ids)
            managementModels.showInfo('Aviso', message)
        except Exception as e:
            managementModels.showError('Aviso', str(e))
        finally:
            managementModels.addRows(self.getSapModels())

    def getSapRules(self, parent=None):
        try:
            return self.sapCtrl.getRules()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def getSapRuleSet(self, parent=None):
        try:
            return self.sapCtrl.getRuleSet()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def openManagementRules(self):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        if managementRules.isVisible():
            managementRules.toTopLevel()
            return
        sapRules = self.getSapRules(parent=managementRules)
        for ruleData in sapRules:
            ruleData['qgisExpressionWidget'] = self.getQgisLineEditExpression()
        managementRules.addRows(sapRules)
        managementRules.show()

    def getQgisLineEditExpression(self):
        return self.qgis.getWidgetByName('lineEditExpression')

    def addRules(self):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        addRuleForm = self.widgetFactory.create(
            'AddRuleForm',
            self.getQgisLineEditExpression(),
            parent=managementRules
        )
        addRuleForm.setGroupList(
            self.getSapRuleSet(parent=self)
        )
        addRuleForm.setLayerList(self.getSapLayers())
        if not addRuleForm.exec():
            return
        inputRuleData = addRuleForm.getData()
        self.createSapRules([inputRuleData])

    def createSapRules(self, rulesData):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        try:
            message = self.sapCtrl.createRules(rulesData)
            self.showInfoMessageBox(managementRules, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementRules, 'Aviso', str(e))
        sapRules = self.getSapRules(parent=managementRules)
        for ruleData in sapRules:
            ruleData['qgisExpressionWidget'] = self.getQgisLineEditExpression()
        managementRules.addRows(sapRules)

    def updateSapRules(self, rulesData):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        try:
            message = self.sapCtrl.updateRules(rulesData)
            self.showInfoMessageBox(managementRules, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementRules, 'Aviso', str(e))
        sapRules = self.getSapRules(parent=managementRules)
        for ruleData in sapRules:
            ruleData['qgisExpressionWidget'] = self.getQgisLineEditExpression()
        managementRules.addRows(sapRules)

    def deleteSapRules(self, rulesData):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        try:
            message = self.sapCtrl.deleteRules(rulesData)
            self.showInfoMessageBox(managementRules, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementRules, 'Aviso', str(e))
        sapRules = self.getSapRules(parent=managementRules)
        for ruleData in sapRules:
            ruleData['qgisExpressionWidget'] = self.getQgisLineEditExpression()
        managementRules.addRows(sapRules)

    def openManagementRuleSet(self):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        managementRuleSet = self.widgetFactory.create('ManagementRuleSet', self, managementRules)
        managementRuleSet.addRows(
            self.getSapRuleSet()
        )
        managementRuleSet.exec()

    def addRuleSet(self):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        managementRuleSet = self.widgetFactory.create('ManagementRuleSet', self, managementRules)
        addRuleSetForm = self.widgetFactory.create(
            'AddRuleSetForm',
            parent=managementRuleSet
        )
        if not addRuleSetForm.exec():
            return
        inputRuleSetData = addRuleSetForm.getData()
        self.createSapRuleSet([inputRuleSetData])

    def createSapRuleSet(self, data):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        managementRuleSet = self.widgetFactory.create('ManagementRuleSet', self, managementRules)
        try:
            message = self.sapCtrl.createRuleSet(data)
            self.showInfoMessageBox(managementRuleSet, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementRuleSet, 'Aviso', str(e))
        managementRuleSet.addRows( self.getSapRuleSet() )

    def updateSapRuleSet(self, data):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        managementRuleSet = self.widgetFactory.create('ManagementRuleSet', self, managementRules)
        try:
            message = self.sapCtrl.updateRuleSet(data)
            self.showInfoMessageBox(managementRules, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementRules, 'Aviso', str(e))
        managementRuleSet.addRows( self.getSapRuleSet() )
    
    def deleteSapRuleSet(self, ids):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        managementRuleSet = self.widgetFactory.create('ManagementRuleSet', self, managementRules)
        try:
            message = self.sapCtrl.deleteRuleSet(ids)
            self.showInfoMessageBox(managementRules, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementRules, 'Aviso', str(e))
        managementRuleSet.addRows( self.getSapRuleSet() )
    
    def importRulesCsv(self):
        managementRules = self.widgetFactory.create('ManagementRules', self)
        addRulesCsvForm = self.widgetFactory.create('AddRulesCsvForm', self, parent=managementRules)
        if not addRulesCsvForm.exec():
            return
        currentGroupRules = [ d['grupo_regra'].lower() for d in managementRules.getGroupData()]
        rules = self.widgetFactory.create('Rules')
        newRules = rules.getRulesFromCsv(addRulesCsvForm.getData()['pathRulesCsv'])
        for groupRule in newRules:
            if not ( groupRule.lower() in currentGroupRules):
                groupData = managementRules.getGroupData()
                groupData.append({
                    'grupo_regra' : groupRule,
                    'cor_rgb' : newRules[groupRule]['cor_rgb'],
                    'ordem' : newRules[groupRule]['ordem']
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
                    self.getQgisLineEditExpression()
                )
        self.showInfoMessageBox(managementRules, 'Aviso', 'Regras carregadas!')

    def downloadCsvRulesTemplate(self, destPath):
        rules = self.widgetFactory.create('Rules')
        rules.saveTemplateCsv(destPath)
    
    def downloadSapQgisProject(self, destPath):
        self.sapCtrl.downloadQgisProject(destPath)

    def loadLayersQgisProject(self, projectInProgress):
        try:
            layersData = self.sapCtrl.getLayersQgisProject(projectInProgress)
            if layersData['views']:
                self.showInfoMessageBox(self.dockSap, 'Aviso', 'Sem views!')
                return
            dbName = layersData['banco_dados']['nome_db']
            dbHost = layersData['banco_dados']['servidor']
            dbPort = layersData['banco_dados']['porta']
            dbUser = layersData['banco_dados']['login']
            dbPassword = layersData['banco_dados']['senha']
            groupBase = self.qgis.addLayerGroup('Acompanhamento')
            groupProduction = self.qgis.addLayerGroup('Linha de produção', groupBase)
            groupPhase = self.qgis.addLayerGroup('Fase', groupBase)
            groupSubPhase = self.qgis.addLayerGroup('Subfase', groupBase)
            for viewData in layersData['views']:
                """ if viewData['tipo'] == 'fase':
                    groupParent = groupPhase
                elif viewData['tipo'] == 'subfase':
                    groupParent = groupSubPhase
                else:
                    groupParent = groupProduction
                groupProject = self.qgis.addLayerGroup(viewData['projeto'], groupParent) """
                self.qgis.loadLayer(
                    dbName, 
                    dbHost, 
                    dbPort, 
                    dbUser, 
                    dbPassword, 
                    viewData['schema'], 
                    viewData['nome'], 
                    #groupProject
                )
        except Exception as e:
            self.showErrorMessageBox(self.dockSap, 'Aviso', str(e))

    def activeRemoveByClip(self):
        self.qgis.activeMapToolByToolName('removeByClip')

    def activeRemoveByIntersect(self):
        self.qgis.activeMapToolByToolName('removeByIntersect')

    def openManagementUsersPrivileges(self):
        managementUsersPrivileges = self.widgetFactory.create('ManagementUsersPrivileges', self)
        if managementUsersPrivileges.isVisible():
            managementUsersPrivileges.toTopLevel()
            return
        managementUsersPrivileges.addRows( self.getSapUsers(parent=managementUsersPrivileges) )
        managementUsersPrivileges.show()

    def getSapUsers(self, parent=None):
        try:
            return self.sapCtrl.getUsers()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def updateUsersPrivileges(self, usersData):
        managementUsersPrivileges = self.widgetFactory.create('ManagementUsersPrivileges', self)
        try:
            message = self.sapCtrl.updateUsersPrivileges(usersData)
            self.showInfoMessageBox(managementUsersPrivileges, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementUsersPrivileges, 'Aviso', str(e)) 
        managementUsersPrivileges.addRows( self.getSapUsers(parent=managementUsersPrivileges) )
    
    def openManagementImportLayers(self):
        managementImportLayers = self.widgetFactory.create('ManagementImportLayers', self)
        if managementImportLayers.isVisible():
            managementImportLayers.toTopLevel()
            return
        managementImportLayers.show()

    def loadManagementImportLayers(self, dbHost, dbPort, dbName):
        managementImportLayers = self.widgetFactory.create('ManagementImportLayers', self)
        postgresLayers = self.getLayersFromPostgres(dbHost, dbPort, dbName)
        layersRows = []
        sapLayers = self.getSapLayers(parent=managementImportLayers)
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
        managementImportLayers.addRows(layersRows)

    def getSapLayers(self, parent=None):
        try:
            return self.sapCtrl.getLayers()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def importLayers(self, layersImported):
        managementImportLayers = self.widgetFactory.create('ManagementImportLayers', self)
        try:
            message = self.sapCtrl.importLayers(layersImported)
            self.showInfoMessageBox(managementImportLayers, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementImportLayers, 'Aviso', str(e))
        dbName = managementImportLayers.getCurrentDatabase()
        dbData = managementImportLayers.getDatabaseData(dbName)
        if not ( dbData is None ):
            self.loadManagementImportLayers(
                dbData['servidor'],
                dbData['porta'],
                dbData['nome']
            )

    def getLayersFromPostgres(self, dbHost, dbPort, dbName):
        managementImportLayers = self.widgetFactory.create('ManagementImportLayers', self)
        try:
            postgres = self.databasesFactory.getDatabase('Postgresql')
            auth = self.sapCtrl.getAuthDatabase()
            postgres.setConnection(dbName, dbHost, dbPort, auth['login'], auth['senha'])
            return postgres.getLayers()
        except Exception as e:
            self.showErrorMessageBox(managementImportLayers, 'Aviso', str(e))
        return []

    def openManagementEditLayers(self):
        managementEditLayers = self.widgetFactory.create('ManagementEditLayers', self)
        if managementEditLayers.isVisible():
            managementEditLayers.toTopLevel()
            return
        managementEditLayers.addRows(self.getSapLayers(parent=managementEditLayers))
        managementEditLayers.show()

    def updateLayers(self, layersData):
        managementEditLayers = self.widgetFactory.create('ManagementEditLayers', self)
        self.sapCtrl.updateLayers(layersData)
        managementEditLayers.addRows(self.getSapLayers(parent=managementEditLayers))

    def deleteLayers(self, deletedLayersIds):
        managementEditLayers = self.widgetFactory.create('ManagementEditLayers', self)
        self.sapCtrl.deleteLayers(deletedLayersIds)
        managementEditLayers.addRows(self.getSapLayers(parent=managementEditLayers))

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
            postgres = self.databasesFactory.getDatabase('Postgresql')
            auth = self.sapCtrl.getAuthDatabase()
            postgres.setConnection(dbName, dbHost, dbPort, auth['login'], auth['senha'])
            if copyStyles:
                postgres.insertStyles(self.getSapStyles(parent=self.dockSap))
            if copyModels:
                postgres.insertModels(self.getSapModels(parent=self.dockSap))
            if copyRules:
                postgres.insertRuleGroups( self.getSapRuleSet(parent=self.dockSap) )
                postgres.insertRules( self.getSapRules(parent=self.dockSap) )
            if copyMenus:
                postgres.insertMenus(self.getSapMenus(parent=self.dockSap))
            self.showInfoMessageBox(self.dockSap, 'Aviso', "Dados copiados!")
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def getSapMenus(self, parent=None):
        try:
            return self.sapCtrl.getMenus()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def openManagementFmeServers(self):
        managementFmeServers = self.widgetFactory.create('ManagementFmeServers', self)
        if managementFmeServers.isVisible():
            managementFmeServers.toTopLevel()
            return
        managementFmeServers.addRows(self.getSapFmeServers())
        managementFmeServers.show()

    def getSapFmeServers(self, parent=None):
        try:
            return self.sapCtrl.getFmeServers()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def addFmeServer(self):
        managementFmeServers = self.widgetFactory.create('ManagementFmeServers', self)
        addFmeServerForm = self.widgetFactory.create('AddFmeServerForm', parent=managementFmeServers)
        if not addFmeServerForm.exec():
            return
        inputFmeServerData = addFmeServerForm.getData()
        self.createFmeServers([inputFmeServerData])

    def createFmeServers(self, fmeServers):
        managementFmeServers = self.widgetFactory.create('ManagementFmeServers', self)
        try:
            message = self.sapCtrl.createFmeServers(fmeServers)
            self.showInfoMessageBox(managementFmeServers, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeServers, 'Aviso', str(e))
        managementFmeServers.addRows(self.getSapFmeServers(parent=managementFmeServers))

    def deleteFmeServers(self, fmeServersIds):
        managementFmeServers = self.widgetFactory.create('ManagementFmeServers', self)
        try:
            message = self.sapCtrl.deleteFmeServers(fmeServersIds)
            self.showInfoMessageBox(managementFmeServers, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeServers, 'Aviso', str(e))
        managementFmeServers.addRows(self.getSapFmeServers(parent=managementFmeServers))

    def updateFmeServers(self, fmeServers):
        managementFmeServers = self.widgetFactory.create('ManagementFmeServers', self)
        try:
            message = self.sapCtrl.updateFmeServers(fmeServers)
            self.showInfoMessageBox(managementFmeServers, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeServers, 'Aviso', str(e))
        managementFmeServers.addRows(self.getSapFmeServers(parent=managementFmeServers))

    def openManagementFmeProfiles(self):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        managementFmeServers = self.widgetFactory.create('ManagementFmeServers', self)
        managementFmeProfiles.setFmeServers(self.getSapFmeServers(parent=managementFmeServers))
        managementFmeProfiles.setSubphases(self.getSapSubphases())
        if managementFmeProfiles.isVisible():
            managementFmeProfiles.toTopLevel()
            return
        managementFmeProfiles.addRows(self.getSapFmeProfiles())
        managementFmeProfiles.show()

    def getSapSubphases(self):
        return self.sapCtrl.getSubphases()

    def getSapFmeProfiles(self):
        return self.sapCtrl.getFmeProfiles()

    def getFmeRoutines(self, server, port):
        try:
            return self.fmeCtrl.getRoutines(server, port)
        except Exception as e:
            self.showErrorMessageBox(self.dockSap, 'Aviso', 'Erro ao buscar rotinas no servidor do FME. Verifique se o servidor está ativo.')
            return []

    def addFmeProfile(self):
        managementFmeProfiles = self.widgetFactory.create('ManagementFmeProfiles', self)
        addFmeProfileForm = self.widgetFactory.create('AddFmeProfileForm', self, parent=managementFmeProfiles)
        addFmeProfileForm.loadFmeServers(self.getSapFmeServers())
        addFmeProfileForm.loadSubphases(self.getSapSubphases())
        if not addFmeProfileForm.exec():
            return
        inputFmeProfileData = addFmeProfileForm.getData()
        self.createFmeProfiles([inputFmeProfileData])

    def createFmeProfiles(self, fmeProfiles):
        managementFmeProfiles = self.widgetFactory.create('ManagementFmeProfiles', self)
        try:
            message = self.sapCtrl.createFmeProfiles(fmeProfiles)
            self.showInfoMessageBox(managementFmeProfiles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeProfiles, 'Aviso', str(e))
        managementFmeProfiles.addRows(self.getSapFmeProfiles())

    def deleteFmeProfiles(self, fmeProfilesIds):
        managementFmeProfiles = self.widgetFactory.create('ManagementFmeProfiles', self)
        try:
            message = self.sapCtrl.deleteFmeProfiles(fmeProfilesIds)
            self.showInfoMessageBox(managementFmeProfiles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeProfiles, 'Aviso', str(e))
        managementFmeProfiles.addRows(self.getSapFmeProfiles())

    def updateFmeProfiles(self, fmeProfiles):
        managementFmeProfiles = self.widgetFactory.create('ManagementFmeProfiles', self)
        try:
            message = self.sapCtrl.updateFmeProfiles(fmeProfiles)
            self.showInfoMessageBox(managementFmeProfiles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeProfiles, 'Aviso', str(e))
        managementFmeProfiles.addRows(self.sapCtrl.getFmeProfiles())

    def getSapStepsByFeatureId(self, featureId):
        subphaseId = self.qgis.getActiveLayerAttribute(featureId, 'subfase_id')
        return self.getSapStepsByTag(tag='nome', tagFilter=('subfase_id', subphaseId))

    def getSapStepsByTag(self, tag, withDuplicate=False, numberTag='', tagFilter=('', ''), sortByTag=''):
        def defaultOrder(elem):
            return elem['ordem']
        def atoi(text):
            return int(text) if text.isdigit() else text
        def orderBy(elem):
            return [ atoi(c) for c in re.split(r'(\d+)', elem[sortByTag].lower()) ]
        steps = self.sapCtrl.getSteps()
        steps.sort(key=defaultOrder)  
        selectedSteps = []   
        for step in steps:
            value = step[tag]
            tagTest = [ t[tag] for t in selectedSteps if str(value).lower() in str(t[tag]).lower() ]
            if not(withDuplicate) and tagTest:
                continue
            if numberTag:
                number = len([ t for t in selectedSteps if str(step[numberTag]).lower() in str(t[numberTag]).lower() ]) + 1
                step[numberTag] = "{0} {1}".format(step[numberTag], number)
            selectedSteps.append(step)
        if sortByTag:
            selectedSteps.sort(key=orderBy)
        if tagFilter[0] and tagFilter[1]:
            selectedSteps = [ s for s in selectedSteps if s[tagFilter[0]] == tagFilter[1]]   
        return selectedSteps

    def getQgisComboBoxPolygonLayer(self):
        return self.qgis.getWidgetByName('comboBoxPolygonLayer')

    def createSapProducts(self, layer, productionLineId, associatedFields, onlySelected):
        features = self.qgis.dumpFeatures(layer, onlySelected)
        products = []
        for feat in features:
            data = {}
            for field in associatedFields:
                data[field] = str(feat[ associatedFields[field] ])
            data['geom'] = self.qgis.geometryToEwkt( feat['geometry'], layer.crs().authid(), 'EPSG:4326' )
            products.append(data)
        invalidProducts = [ p for p in products if not p['escala'] ]
        if invalidProducts:
            Exception('Há feições com dados nulo. Para criar produtos as feições não podem ter escala nula.')
        try:
            message = self.sapCtrl.createProducts(productionLineId, products)
            self.showInfoMessageBox(None, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(None, 'Aviso', str(e))

    def loadSapWorkUnits(self, layer, subphaseId, onlySelected, associatedFields):
        features = self.qgis.dumpFeatures(layer, onlySelected)
        fieldsType = {
            'disponivel' : bool,
            'dado_producao_id' : int,
            'lote_id' : int,
            'prioridade' : int
        }
        workUnits = []
        for feat in features:
            data = {}
            for field in associatedFields:
                value = str(feat[ associatedFields[field]])
                data[field] = fieldsType[field](value) if field in fieldsType else value
            data['geom'] = self.qgis.geometryToEwkt( feat['geometry'], layer.crs().authid(), 'EPSG:4326' )
            workUnits.append(data)
        invalidWorkUnits = [ 
            p for p in workUnits 
            if not (
                p['nome'] and p['epsg'] and p['dado_producao_id'] 
                and 
                p['disponivel'] and p['prioridade'] and p['lote_id']
            ) 
        ]
        if invalidWorkUnits:
            self.showErrorMessageBox(self.dockSap, 'Aviso', 'Há feições com dados nulo. Para carregar unidades de trabalho as feições só podem ter a observação nula.')
            return
        try:
            message = self.sapCtrl.loadWorkUnit(subphaseId, workUnits)
            self.showInfoMessageBox(None, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(None, 'Aviso', str(e))

    def advanceSapActivityToNextStep(self, activityIds, endStep):
        self.sapCtrl.advanceActivityToNextStep(
            activityIds, 
            endStep
        )

    def getSapLots(self):
        return self.sapCtrl.getLots()

    def alterSapLot(self, workspacesIds, lotId):
        self.sapCtrl.alterLot(workspacesIds, lotId)

    def getSapAssociationStrategies(self):
        return self.sapCtrl.getAssociationStrategies()

    def associateSapInputs(self, workspacesIds, inputGroupId, associationStrategyId, defaultPath):
        self.sapCtrl.associateInputs(workspacesIds, inputGroupId, associationStrategyId, defaultPath)

    def deleteSapUserActivities(self, userId):
        self.sapCtrl.deleteUserActivities(userId)

    def copySapWorkUnit(self, workspacesIds, stepIds, associateInputs):
        self.sapCtrl.copyWorkUnit(workspacesIds, stepIds, associateInputs)

    def createSapActivities(self, workspacesIds, stepId):
        self.sapCtrl.createActivities(workspacesIds, stepId )

    def getSapProductionProfiles(self):
        return self.sapCtrl.getProductionProfiles()

    def createSapPriorityGroupActivity(self, activityIds, priority, profileId):
        self.sapCtrl.createPriorityGroupActivity(
            activityIds, 
            priority, 
            profileId
        )

    def getSapProductionLines(self):
        return self.sapCtrl.getProductionLines()

    def deleteSapActivities(self, activityIds):
        self.sapCtrl.deleteActivities(
            activityIds
        )

    def deleteSapAssociatedInputs(self, workspacesIds, inputGroupId):
        self.sapCtrl.deleteAssociatedInputs(workspacesIds, inputGroupId) 

    def deleteSapWorkUnits(self, workspacesIds):
        self.sapCtrl.deleteWorkUnits(workspacesIds)       

    def fillSapCommentActivity(self, activityIds, commentActivity, commentWorkspace):
        self.sapCtrl.fillCommentActivity(
            activityIds, 
            commentActivity, 
            commentWorkspace
        )

    def getSapCommentsByActivity(self, activityId):
        return self.sapCtrl.getCommentsByActivity(activityId)

    def getSapUsersFromAuthService(self):
        return self.sapCtrl.getUsersFromAuthService()

    def importSapUsersAuthService(self, usersIds):
        return self.sapCtrl.importUsersAuthService(usersIds)

    def lockSapWorkspace(self, workspacesIds):
        self.sapCtrl.lockWorkspace(workspacesIds)

    def openSapActivity(self, activityId):
        try:
            self.qgis.startSapFP(
                self.sapCtrl.getActivityDataById(activityId)
            )
        except Exception as e:
            self.showErrorMessageBox(None, 'Aviso', str(e))
        
    def openSapNextActivityByUser(self, userId, nextActivity):
        try:
            self.sapCtrl.getNextActivityDataByUser(userId, nextActivity)
            activityData = self.sapCtrl.getNextActivityDataByUser(userId, nextActivity)
            if not activityData['dados']:
                raise Exception('Usuário sem atividades!')
            self.qgis.startSapFP(
                activityData
            )
        except Exception as e:
            self.showErrorMessageBox(None, 'Aviso', str(e))

    def pauseSapActivity(self, workspacesIds):
        self.sapCtrl.pauseActivity(workspacesIds)

    def resetSapPrivileges(self):
        self.sapCtrl.resetPrivileges()

    def restartSapActivity(self, workspacesIds):
        self.sapCtrl.restartActivity(workspacesIds)

    def returnSapActivityToPreviousStep(self, activityIds, preserveUser):
        self.sapCtrl.returnActivityToPreviousStep(activityIds, preserveUser)

    def revokeSapPrivileges(self, dbHost, dbPort, dbName):
        self.sapCtrl.revokePrivileges(dbHost, dbPort, dbName)

    def setSapPriorityActivity(self, activityIds, priority, userId):
        self.sapCtrl.setPriorityActivity(activityIds, priority, userId)

    def synchronizeSapUserInformation(self):
        self.sapCtrl.synchronizeUserInformation()

    def unlockSapWorkspace(self, workspacesIds):
        self.sapCtrl.unlockWorkspace(workspacesIds)
    
    def updateSapBlockedActivities(self):
        self.sapCtrl.updateBlockedActivities()

    def getSapDatabases(self):
        return self.sapCtrl.getDatabases()

    def getSapInputGroups(self):
        return self.sapCtrl.getInputGroups()

    def getSapModelProfiles(self):
        try:
            return self.sapCtrl.getModelProfiles()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def openManagementModelProfiles(self):
        managementModelProfiles = self.widgetFactory.create('ManagementModelProfiles', self)
        managementModelProfiles.setModels(self.getSapModels())
        managementModelProfiles.setSubphases(self.getSapSubphases())
        if managementModelProfiles.isVisible():
            managementModelProfiles.toTopLevel()
            return
        managementModelProfiles.addRows(self.getSapModelProfiles())
        managementModelProfiles.show()

    def addModelProfile(self):
        managementModelProfiles = self.widgetFactory.create('ManagementModelProfiles', self)
        addModelProfileForm = self.widgetFactory.create('AddModelProfileForm', parent=managementModelProfiles)
        addModelProfileForm.loadSubphases(self.getSapSubphases())
        addModelProfileForm.loadModels(self.getSapModels())
        if not addModelProfileForm.exec():
            return
        inputModelProfileData = addModelProfileForm.getData()
        self.createSapModelProfiles([inputModelProfileData])
        managementModelProfiles.adjustColumns()

    def createSapModelProfiles(self, data):
        managementModelProfiles = self.widgetFactory.create('ManagementModelProfiles', self)
        try:
            message = self.sapCtrl.createModelProfiles(data)
            managementModelProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementModelProfiles.showError('Aviso', str(e))
        finally:
            managementModelProfiles.addRows(self.getSapModelProfiles())

    def updateSapModelProfiles(self, data):
        managementModelProfiles = self.widgetFactory.create('ManagementModelProfiles', self)
        try:
            message = self.sapCtrl.updateModelProfiles(data)
            managementModelProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementModelProfiles.showError('Aviso', str(e))
        finally:
            managementModelProfiles.addRows(self.getSapModelProfiles())

    def deleteSapModelProfiles(self, ids):
        managementModelProfiles = self.widgetFactory.create('ManagementModelProfiles', self)
        try:
            message = self.sapCtrl.deleteModelProfiles(ids)
            managementModelProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementModelProfiles.showError('Aviso', str(e))
        finally:
            #print(self.getSapModelProfiles())
            managementModelProfiles.addRows(self.getSapModelProfiles())

    def getSapRuleProfiles(self):
        try:
            return self.sapCtrl.getRuleProfiles()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def openManagementRuleProfiles(self):
        managementRuleProfiles = self.widgetFactory.create('ManagementRuleProfiles', self)
        managementRuleProfiles.setGroupData(self.getSapRuleSet())
        managementRuleProfiles.setSubphases(self.getSapSubphases())
        if managementRuleProfiles.isVisible():
            managementRuleProfiles.toTopLevel()
            return
        managementRuleProfiles.addRows(self.getSapRuleProfiles())
        managementRuleProfiles.show()

    def addRuleProfile(self):
        managementRuleProfiles = self.widgetFactory.create('ManagementRuleProfiles', self)
        addRuleProfileForm = self.widgetFactory.create('AddRuleProfileForm', parent=managementRuleProfiles)
        addRuleProfileForm.loadSubphases(self.getSapSubphases())
        addRuleProfileForm.loadRuleGroups(self.getSapRuleSet())
        if not addRuleProfileForm.exec():
            return
        inputRuleProfileData = addRuleProfileForm.getData()
        self.createSapRuleProfiles([inputRuleProfileData])
        managementRuleProfiles.adjustColumns()

    def createSapRuleProfiles(self, data):
        managementRuleProfiles = self.widgetFactory.create('ManagementRuleProfiles', self)
        try:
            message = self.sapCtrl.createRuleProfiles(data)
            managementRuleProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementRuleProfiles.showError('Aviso', str(e))
        finally:
            managementRuleProfiles.addRows(self.getSapRuleProfiles())

    def updateSapRuleProfiles(self, data):
        managementRuleProfiles = self.widgetFactory.create('ManagementRuleProfiles', self)
        try:
            message = self.sapCtrl.updateRuleProfiles(data)
            managementRuleProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementRuleProfiles.showError('Aviso', str(e))
        finally:
            managementRuleProfiles.addRows(self.getSapRuleProfiles())

    def deleteSapRuleProfiles(self, ids):
        managementRuleProfiles = self.widgetFactory.create('ManagementRuleProfiles', self)
        try:
            message = self.sapCtrl.deleteRuleProfiles(ids)
            managementRuleProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementRuleProfiles.showError('Aviso', str(e))
        finally:
            #print(self.getSapModelProfiles())
            managementRuleProfiles.addRows(self.getSapRuleProfiles())

    def getSapStyleNames(self):
        try:
            return self.sapCtrl.getStyleNames()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def getSapStyleProfiles(self):
        try:
            return self.sapCtrl.getStyleProfiles()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def openManagementStyleProfiles(self):
        managementStyleProfiles = self.widgetFactory.create('ManagementStyleProfiles', self)
        managementStyleProfiles.setSubphases(self.getSapSubphases())
        managementStyleProfiles.setStyles(self.getSapStyleNames())
        if managementStyleProfiles.isVisible():
            managementStyleProfiles.toTopLevel()
            return
        managementStyleProfiles.addRows(self.getSapStyleProfiles())
        managementStyleProfiles.show()

    def addStyleProfile(self):
        managementStyleProfiles = self.widgetFactory.create('ManagementStyleProfiles', self)
        addStyleProfile = AddStyleProfileFoself.widgetFactory.create('AddStyleProfileForm', parent=managementStyleProfiles)
        addStyleProfile.loadSubphases(self.getSapSubphases())
        addStyleProfile.loadStyles(self.getSapStyleNames())
        if not addStyleProfile.exec():
            return
        inputStyleProfileData = addStyleProfile.getData()
        self.createSapStyleProfiles([inputStyleProfileData])
        managementStyleProfiles.adjustColumns()

    def createSapStyleProfiles(self, data):
        managementStyleProfiles = self.widgetFactory.create('ManagementStyleProfiles', self)
        try:
            message = self.sapCtrl.createStyleProfiles(data)
            managementStyleProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementStyleProfiles.showError('Aviso', str(e))
        finally:
            managementStyleProfiles.addRows(self.getSapStyleProfiles())

    def updateSapStyleProfiles(self, data):
        managementStyleProfiles = self.widgetFactory.create('ManagementStyleProfiles', self)
        try:
            message = self.sapCtrl.updateStyleProfiles(data)
            managementStyleProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementStyleProfiles.showError('Aviso', str(e))
        finally:
            managementStyleProfiles.addRows(self.getSapStyleProfiles())

    def deleteSapStyleProfiles(self, ids):
        managementStyleProfiles = self.widgetFactory.create('ManagementStyleProfiles', self)
        try:
            message = self.sapCtrl.deleteStyleProfiles(ids)
            managementStyleProfiles.showInfo('Aviso', message)
        except Exception as e:
            managementStyleProfiles.showError('Aviso', str(e))
        finally:
            managementStyleProfiles.addRows(self.getSapStyleProfiles())

    def getScreenLayers(self, functionName, fieldName):
        selectedlayers = self.qgis.getSelectedLayersTreeView()
        layerSettings = self.functionsSettings.getSettings(functionName, fieldName)
        values = []
        try:
            for layer in selectedlayers:
                for layerOptions in layerSettings:
                    if ( 
                            layerOptions['layerName'] != '*' and 
                            not( layerOptions['layerName'] in layer.name() ) 
                        ):
                        continue
                    values.append( layer.name() )
                    break
            return ",".join([ name for name in values ])
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return ''    

    def createScreens(self, primaryLayerNames, secundaryLayerNames):
        for primaryLayerName in primaryLayerNames:
            layers = [ primaryLayerName ] + secundaryLayerNames
            self.qgis.createScreens( layers )

    def getSapProjects(self):
        return self.sapCtrl.getProjects()

    def openAssociateUserToProjects(self, parent):
        if self.assocUserToProjDlg and not sip.isdeleted(self.assocUserToProjDlg):
            self.assocUserToProjDlg.close()
        self.assocUserToProjDlg = self.widgetFactory.create('AssociateUserToProjects', self, parent)
        self.assocUserToProjDlg.loadUsers( self.sapCtrl.getUsers() )
        self.assocUserToProjDlg.updateProjectTable()
        self.assocUserToProjDlg.show()

    def openAddUserProject(self, userId, parent, callback):
        if self.addProjDlg and not sip.isdeleted(self.addProjDlg):
            self.addProjDlg.close()
        self.addProjDlg = self.widgetFactory.create('AddUserProject', self, parent)
        self.addProjDlg.setUserId(userId)
        self.addProjDlg.loadProjects(self.getSapProjects())
        self.addProjDlg.update.connect(callback)
        self.addProjDlg.show()

    def openEditUserProject(self, userId, data, parent, callback):
        if self.addProjDlg and not sip.isdeleted(self.addProjDlg):
            self.addProjDlg.close()
        self.addProjDlg = self.widgetFactory.create('AddUserProject', self, parent)
        self.addProjDlg.setUserId(userId)
        self.addProjDlg.activeEditMode(True)
        self.addProjDlg.loadProjects(self.getSapProjects())
        self.addProjDlg.setCurrentId(data['id'])
        self.addProjDlg.setData(data)
        self.addProjDlg.update.connect(callback)
        self.addProjDlg.show()

    def getSapUserProject(self):
        data = self.sapCtrl.getUserProjectProduction()
        projects = self.getSapProjects()
        for d in data:
            project = next((p for p in projects if p['id'] == d['projeto_id']), None)
            if project:
                d['projeto'] = project['nome']
        return data

    def createSapUserProject(self, data, parent):
        parent = parent if parent else self.qgis.getMainWindow()
        try:
            self.sapCtrl.createUserProjectProduction(data)
            self.showInfoMessageBox(parent, 'Aviso', 'Relacionamento atualizado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))

    def updateSapUserProject(self, data, parent):
        parent = parent if parent else self.qgis.getMainWindow()
        try:
            self.sapCtrl.updateUserProjectProduction(data)
            self.showInfoMessageBox(parent, 'Aviso', 'Relacionamento atualizado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))

    def deleteSapUserProject(self, data, parent):
        parent = parent if parent else self.qgis.getMainWindow()
        try:
            self.sapCtrl.deleteUserProjectProduction(data)
            self.showInfoMessageBox(parent, 'Aviso', 'Relacionamento atualizado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))

    def openAssociateUserToProfiles(self, parent):
        if self.assocUserToProfDlg and not sip.isdeleted(self.assocUserToProfDlg):
            self.assocUserToProfDlg.close()
        self.assocUserToProfDlg = self.widgetFactory.create('AssociateUserToProfiles', self, parent)
        self.assocUserToProfDlg.loadUsers( self.sapCtrl.getUsers() )
        self.assocUserToProfDlg.show()

    def openAddUserProfileProduction(self, userId, parent, callback):
        if self.addProfProdDlg and not sip.isdeleted(self.addProfProdDlg):
            self.addProfProdDlg.close()
        self.addProfProdDlg = self.widgetFactory.create('AddUserProfileProduction', self, parent)
        self.addProfProdDlg.setUserId(userId)
        self.addProfProdDlg.loadProfiles( self.getSapProductionProfiles() )
        self.addProfProdDlg.save.connect(callback)
        self.addProfProdDlg.show()

    def openEditUserProfileProduction(self, userId, data, parent, callback):
        if self.addProfProdDlg and not sip.isdeleted(self.addProfProdDlg):
            self.addProfProdDlg.close()
        self.addProfProdDlg = self.widgetFactory.create('AddUserProfileProduction', self, parent)
        self.addProfProdDlg.setUserId(userId)
        self.addProfProdDlg.loadProfiles( self.getSapProductionProfiles() )
        self.addProfProdDlg.activeEditMode(True)
        self.addProfProdDlg.setCurrentId(data['id'])
        self.addProfProdDlg.setData(data)
        self.addProfProdDlg.update.connect(callback)
        self.addProfProdDlg.show()

    def openProductionProfileRelation(self, parent, callback):
        if self.userProfManDlg and not sip.isdeleted(self.userProfManDlg):
            self.userProfManDlg.close()
        self.userProfManDlg = self.widgetFactory.create(
            'ProfileProductionSetting', 
            self, 
            parent
        )
        self.userProfManDlg.loadProfiles( self.getSapProductionProfiles() )
        self.userProfManDlg.save.connect(callback)
        self.userProfManDlg.show()

    def openAddProfileProductionSetting(self, parent, callback):
        if self.aProfProdRelDlg and not sip.isdeleted(self.aProfProdRelDlg):
            self.aProfProdRelDlg.close()
        self.aProfProdRelDlg = self.widgetFactory.create(
            'AddProfileProductionSetting', 
            self,
            parent
        )
        self.aProfProdRelDlg.loadSubphases( self.getSapSubphases() )
        self.aProfProdRelDlg.loadSteps( self.getSapStepType() )
        self.aProfProdRelDlg.save.connect(callback)
        self.aProfProdRelDlg.show()

    def openEditProfileProductionSetting(self, data, parent, callback):
        if self.aProfProdRelDlg and not sip.isdeleted(self.aProfProdRelDlg):
            self.aProfProdRelDlg.close()
        self.aProfProdRelDlg = self.widgetFactory.create(
            'AddProfileProductionSetting', 
            self,
            parent
        )
        self.aProfProdRelDlg.loadSubphases( self.getSapSubphases() )
        self.aProfProdRelDlg.loadSteps( self.getSapStepType() )
        self.aProfProdRelDlg.activeEditMode(True)
        self.aProfProdRelDlg.setCurrentId(data['id'])
        self.aProfProdRelDlg.setData(data)
        self.aProfProdRelDlg.save.connect(callback)
        self.aProfProdRelDlg.show()

    def getSapStepType(self):
        return self.sapCtrl.getStepType()

    def openProductionProfileEditor(self, parent, callback):
        if self.userProfEditDlg and not sip.isdeleted(self.userProfEditDlg):
            self.userProfEditDlg.close()
        self.userProfEditDlg = self.widgetFactory.create(
            'ProductionProfileEditor', 
            self,
            parent
        )
        self.userProfEditDlg.loadProfiles( self.getSapProductionProfiles() )
        self.userProfEditDlg.save.connect(callback)
        self.userProfEditDlg.show()

    def openCreateProfileProduction(self, parent, callback):
        if self.cProfProdDlg and not sip.isdeleted(self.cProfProdDlg):
            self.cProfProdDlg.close()
        self.cProfProdDlg = self.widgetFactory.create(
            'CreateProfileProduction', 
            self,
            parent
        )
        self.cProfProdDlg.save.connect(callback)
        self.cProfProdDlg.show()

    def openEditProfileProduction(self, data, parent, callback):
        if self.cProfProdDlg and not sip.isdeleted(self.cProfProdDlg):
            self.cProfProdDlg.close()
        self.cProfProdDlg = self.widgetFactory.create(
            'CreateProfileProduction', 
            self,
            parent
        )
        self.cProfProdDlg.activeEditMode(True)
        self.cProfProdDlg.setData(data)
        self.cProfProdDlg.save.connect(callback)
        self.cProfProdDlg.show()

    def createSapProductionProfiles(self, data, parent):
        self.sapCtrl.createProductionProfiles(data, parent)

    def updateSapProductionProfiles(self, data, parent):
        self.sapCtrl.updateProductionProfiles(data, parent)

    def deleteSapProductionProfiles(self, data, parent):
        self.sapCtrl.deleteProductionProfiles(data, parent)

    def getSapProfileProductionStep(self):
        data = self.sapCtrl.getProfileProductionStep()
        subphases = self.getSapSubphases()
        stepTypes = self.getSapStepType()
        for d in data:
            subphase = next((s for s in subphases if s['subfase_id'] == d['subfase_id']), None)
            if subphase:
                d['subfase'] = subphase['subfase']
            stepType = next((s for s in stepTypes if s['code'] == d['tipo_etapa_id']), None)
            if stepType:
                d['tipo_etapa'] = stepType['nome']
        return data
            
    def createSapProfileProductionStep(self, data, parent):
        parent = parent if parent else self.qgis.getMainWindow()
        try:
            self.sapCtrl.createProfileProductionStep(data)
            self.showInfoMessageBox(parent, 'Aviso', 'Relacionamento criado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        
    def updateSapProfileProductionStep(self, data, parent):
        parent = parent if parent else self.qgis.getMainWindow()
        try:
            self.sapCtrl.updateProfileProductionStep(data)
            self.showInfoMessageBox(parent, 'Aviso', 'Relacionamento atualizado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))

    def deleteSapProfileProductionStep(self, data, parent):
        parent = parent if parent else self.qgis.getMainWindow()
        try:
            self.sapCtrl.deleteProfileProductionStep(data)
            self.showInfoMessageBox(parent, 'Aviso', 'Relacionamento deletado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))

    def getSapUserProfileProduction(self):
        data = self.sapCtrl.getUserProfileProduction()
        profiles = self.getSapProductionProfiles()
        for d in data:
            profile = next((p for p in profiles if p['id'] == d['perfil_producao_id']), None)
            if profile:
                d['perfil_producao'] = profile['nome']
        return data

    def createSapUserProfileProduction(self, data, parent):
        parent = parent if parent else self.qgis.getMainWindow()
        try:
            self.sapCtrl.createUserProfileProduction(data)
            self.showInfoMessageBox(parent, 'Aviso', 'Relacionamento criado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))

    def updateSapUserProfileProduction(self, data, parent):
        parent = parent if parent else self.qgis.getMainWindow()
        try:
            self.sapCtrl.updateUserProfileProduction(data)
            self.showInfoMessageBox(parent, 'Aviso', 'Relacionamento atualizado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))

    def deleteSapUserProfileProduction(self, data, parent):
        parent = parent if parent else self.qgis.getMainWindow()
        try:
            self.sapCtrl.deleteUserProfileProduction(data)
            self.showInfoMessageBox(parent, 'Aviso', 'Relacionamento deletado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))

            