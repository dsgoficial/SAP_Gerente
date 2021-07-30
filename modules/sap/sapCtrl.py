import os
import re

from Ferramentas_Gerencia.modules.sap.interfaces.ISapCtrl import ISapCtrl
from Ferramentas_Gerencia.modules.sap.factories.loginSingleton import LoginSingleton
from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory
from Ferramentas_Gerencia.modules.sap.factories.sapApiSingleton import SapApiSingleton
from Ferramentas_Gerencia.modules.sap.factories.dataModelFactory import DataModelFactory

class SapCtrl(ISapCtrl):

    def __init__(self, 
            qgis, 
            fmeCtrl,
            sapApi=SapApiSingleton.getInstance(),
            loginSingleton=LoginSingleton,
            messageFactory=UtilsFactory().createMessageFactory(),
            dataModelFactory=DataModelFactory()
        ):
        super(SapCtrl, self).__init__()
        self.sapApi = sapApi
        self.qgis = qgis
        self.fmeCtrl = fmeCtrl
        self.messageFactory = messageFactory
        self.activityDataModel = dataModelFactory.createDataModel('SapActivity')
        self.loginView = loginSingleton.getInstance(loginCtrl=self)

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
            server=self.qgis.getSettingsVariable('sapmanager:server')
        )
        return self.loginView.showView()

    def saveLoginData(self, user, password, server):
        self.qgis.setSettingsVariable('sapmanager:user', user)
        self.qgis.setSettingsVariable('sapmanager:password', password)
        self.qgis.setSettingsVariable('sapmanager:server', server)

    def authUser(self, user, password, server):
        try:
            self.sapApi.setServer(server)
            response = self.sapApi.loginAdminUser(
                user, 
                password,
                self.qgis.getVersion(),
                self.qgis.getPluginsVersions()
            )
            self.sapApi.setToken(response['dados']['token'])
            self.loginView.accept()      
        except Exception as e:
            self.showErrorMessageBox(self.loginView, 'Aviso', str(e))
        finally:
            self.saveLoginData(user, password, server)
        return True

    def getUsers(self):
        return self.sapApi.getUsers()

    def getProfiles(self):
        try:
            return self.sapApi.getProfiles()
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))
            return []

    def advanceActivityToNextStep(self, activityIds, endStep):
        try:
            message = self.sapApi.advanceActivityToNextStep(
                activityIds, 
                endStep
            )
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def createPriorityGroupActivity(self, activityIds, priority, profileId):
        try:
            message = self.sapApi.createPriorityGroupActivity(
                activityIds, 
                priority, 
                profileId
            )
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def fillCommentActivity(self, activityIds, commentActivity, commentWorkspace, commentStep, commentSubfase, commentLot):
        try:
            message = self.sapApi.fillCommentActivity(
                activityIds, 
                commentActivity, 
                commentWorkspace, 
                commentStep, 
                commentSubfase,
                commentLot
            )
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def getCommentsByActivity(self, activityId):
        return self.sapApi.getCommentsByActivity(activityId)

    def lockWorkspace(self, workspacesIds):
        try:
            message = self.sapApi.lockWorkspace(workspacesIds)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def loadActivityById(self, activityId):
        acitivityData = self.sapApi.openActivity(activityId)
        acitivityData['user'] = self.qgis.getSettingsVariable('sapmanager:user')
        acitivityData['password'] = self.qgis.getSettingsVariable('sapmanager:password')
        self.activityDataModel.setData(acitivityData)

    def loadNextActivityByUser(self, userId, nextActivity):
        acitivityData = self.sapApi.openNextActivityByUser(userId, nextActivity)
        acitivityData['user'] = self.qgis.getSettingsVariable('sapmanager:user')
        acitivityData['password'] = self.qgis.getSettingsVariable('sapmanager:password')
        self.activityDataModel.setData(acitivityData)

    def getActivity(self):
        return self.activityDataModel

    def isValidActivity(self):
        pass

    def showEndActivityDialog(self, callback):
        pass

    def showReportErrorDialog(self, callback):
        pass

    def pauseActivity(self, workspacesIds):
        try:
            message = self.sapApi.pauseActivity(workspacesIds)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))
    
    def restartActivity(self, workspacesIds):
        try:
            message = self.sapApi.restartActivity(workspacesIds)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))
    
    def returnActivityToPreviousStep(self, activityIds, preserveUser):
        try:
            message = self.sapApi.returnActivityToPreviousStep(activityIds, preserveUser)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def setPriorityActivity(self, activityIds, priority, userId):
        try:
            message = self.sapApi.setPriorityActivity(activityIds, priority, userId)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def unlockWorkspace(self, workspacesIds):
        try:
            message = self.sapApi.unlockWorkspace(workspacesIds)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def updateBlockedActivities(self):
        try:
            message = self.sapApi.updateBlockedActivities()
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def getStyles(self):
        return self.sapApi.getStyles()

    def createStyles(self, data):
        return self.sapApi.createStyles(data)

    def updateStyles(self, data):
        return self.sapApi.updateStyles(data)
    
    def deleteStyles(self, data):
        return self.sapApi.deleteStyles(data)

    def getModels(self):
        return self.sapApi.getModels()

    def createModels(self, modelsData):
        return self.sapApi.createModels(modelsData)

    def updateModels(self, modelsData):
        return self.sapApi.updateModels(modelsData)
    
    def deleteModels(self, modelsData):
        return self.sapApi.deleteModels(modelsData)

    def getRules(self):
        try:
            return self.sapApi.getRules()
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))
            return []

    def createRules(self, data):
        return self.sapApi.createRules(data)

    def updateRules(self, data):
        return self.sapApi.updateRules(data)

    def deleteRules(self, data):
        return self.sapApi.deleteRules(data)

    def getRuleSet(self):
        return self.sapApi.getRuleSet()

    def createRuleSet(self, data):
        return self.sapApi.createRuleSet(data)

    def updateRuleSet(self, data):
        return self.sapApi.updateRuleSet(data)

    def deleteRuleSet(self, data):
        return self.sapApi.deleteRuleSet(data)

    def downloadQgisProject(self, destPath):
        try:
            projectXml = self.sapApi.getQgisProject()
            with open(destPath, 'w') as f:
                f.write(projectXml)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', 'Projeto criado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def getLayersQgisProject(self, projectInProgress):
        return self.sapApi.getLayersQgisProject(projectInProgress)

    def synchronizeUserInformation(self):
        try:
            message = self.sapApi.synchronizeUserInformation()
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def getUsersFromAuthService(self):
        try:
            users = self.sapApi.getUsersFromAuthService()
            return users
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def importUsersAuthService(self, usersIds):
        try:
            message = self.sapApi.importUsersAuthService(usersIds)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def updateUsersPrivileges(self, usersData):
        return self.sapApi.updateUsersPrivileges(usersData)
    
    def deleteActivities(self, activityIds):
        try:
            message = self.sapApi.deleteActivities(
                activityIds
            )
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def createActivities(self, workspacesIds, stepId):
        try:
            message = self.sapApi.createActivities(workspacesIds, stepId )
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def resetPrivileges(self):
        try:
            message = self.sapApi.resetPrivileges()
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def getDatabases(self):
        return self.sapApi.getDatabases()

    def getLayers(self):
        return self.sapApi.getLayers()

    def importLayers(self, layersImported):
        return self.sapApi.importLayers(layersImported)

    def getAuthDatabase(self):
        return self.sapApi.getAuthDatabase()

    def updateLayers(self, layersData):
        try:
            message = self.sapApi.updateLayers(layersData)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def deleteLayers(self, deletedLayersIds):
        try:
            message = self.sapApi.deleteLayers(deletedLayersIds)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def getLots(self):
       return self.sapApi.getLots()

    def alterLot(self, workspacesIds, lotId):
        try:
            message = self.sapApi.alterLot(workspacesIds, lotId)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def revokePrivileges(self, dbHost, dbPort, dbName):
        try:
            message = self.sapApi.revokePrivileges(dbHost, dbPort, dbName)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))
    
    def getMenus(self):
        return self.sapApi.getMenus()

    def getFmeServers(self):
        return self.sapApi.getFmeServers()

    def createFmeServers(self, fmeServers):
        return self.sapApi.createFmeServers(fmeServers)

    def deleteFmeServers(self, fmeServersIds):
        return self.sapApi.deleteFmeServers(fmeServersIds)

    def updateFmeServers(self, fmeServers):
        return self.sapApi.updateFmeServers(fmeServers)

    def getSubphases(self):
        return self.sapApi.getSubphases()

    def getFmeProfiles(self):
        return self.sapApi.getFmeProfiles()

    def createFmeProfiles(self, fmeProfiles):
        return self.sapApi.createFmeProfiles(fmeProfiles)
        
    def deleteFmeProfiles(self, fmeProfilesIds):
        return self.sapApi.deleteFmeProfiles(fmeProfilesIds)

    def updateFmeProfiles(self, fmeProfiles):
        return self.sapApi.updateFmeProfiles(fmeProfiles)

    def getSteps(self):
        return self.sapApi.getSteps()

    def deleteUserActivities(self, userId):
        try:
            message = self.sapApi.deleteUserActivities(userId)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def getInputGroups(self):
        return self.sapApi.getInputGroups()

    def deleteAssociatedInputs(self, workspacesIds, inputGroupId):
        try:
            message = self.sapApi.deleteAssociatedInputs(workspacesIds, inputGroupId)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def deleteWorkUnits(self, workspacesIds):
        try:
            message = self.sapApi.deleteWorkUnits(workspacesIds)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def getProductionLines(self):
        def sortByName(elem):
            return elem['projeto']
        productionLines = self.sapApi.getProductionLines()
        productionLines.sort(key=sortByName)
        return productionLines

    def createProducts(self, productionLineId, products):
        return self.sapApi.createProducts(productionLineId, products)

    def getAssociationStrategies(self):
        return self.sapApi.getAssociationStrategies()

    def associateInputs(self, workspacesIds, inputGroupId, associationStrategyId, defaultPath):
        try:
            message = self.sapApi.associateInputs(workspacesIds, inputGroupId, associationStrategyId, defaultPath)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def loadWorkUnit(self, subphaseId, workUnits):
        return self.sapApi.loadWorkUnit(subphaseId, workUnits)

    def copyWorkUnit(self, workspacesIds, stepIds, associateInputs):
        message = self.sapApi.copyWorkUnit(workspacesIds, stepIds, associateInputs)
        self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', message)
        """ try:
            message = self.sapApi.associateInputs(workspacesIds, inputGroupId, associationStrategyId, defaultPath)
            self.dockSap.showInfo('Aviso', message)
        except Exception as e:
            self.dockSap.showError('Aviso', str(e)) """

    def getModelProfiles(self):
        return self.sapApi.getModelProfiles()

    def createModelProfiles(self, data):
        return self.sapApi.createModelProfiles(data)

    def updateModelProfiles(self, data):
        return self.sapApi.updateModelProfiles(data)

    def deleteModelProfiles(self, data):
        return self.sapApi.deleteModelProfiles(data)

    def getRuleProfiles(self):
        return self.sapApi.getRuleProfiles()

    def createRuleProfiles(self, data):
        return self.sapApi.createRuleProfiles(data)

    def updateRuleProfiles(self, data):
        return self.sapApi.updateRuleProfiles(data)

    def deleteRuleProfiles(self, data):
        return self.sapApi.deleteRuleProfiles(data)

    def getStyleNames(self):
        return self.sapApi.getStyleNames()

    def getStyleProfiles(self):
        return self.sapApi.getStyleProfiles()

    def createStyleProfiles(self, data):
        return self.sapApi.createStyleProfiles(data)

    def updateStyleProfiles(self, data):
        return self.sapApi.updateStyleProfiles(data)

    def deleteStyleProfiles(self, data):
        return self.sapApi.deleteStyleProfiles(data)
            
