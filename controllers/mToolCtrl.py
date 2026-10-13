from qgis.PyQt.QtCore import QObject
from SAP_Gerente.factories.functionsSettingsSingleton import FunctionsSettingsSingleton
from SAP_Gerente.factories.widgetFactory import WidgetFactory
from SAP_Gerente.modules.databases.factories.databasesFactory  import DatabasesFactory
from SAP_Gerente.modules.utils.factories.utilsFactory import UtilsFactory
from SAP_Gerente.modules.dsgTools.factories.processingQgisFactory import ProcessingQgisFactory
from qgis.utils import iface
from qgis import gui, core
from SAP_Gerente.modules.sap.api.contrato import (
    datasetParaCamada, mensagemComRevogacao, revogacaoFalhou
)

from PyQt6 import sip
import os
import re

class MToolCtrl(QObject):

    def __init__(self,
            qgis,
            fmeCtrl,
            sapCtrl,
            databasesFactory=None,
            functionsSettings=None,
            messageFactory=None,
            widgetFactory=None,
            processingFactoryDsgTools=None
        ):
        super(MToolCtrl, self).__init__()
        self.qgis = qgis
        self.fmeCtrl = fmeCtrl
        self.processingFactoryDsgTools = processingFactoryDsgTools or ProcessingQgisFactory()
        self.databasesFactory = databasesFactory or DatabasesFactory()
        self.messageFactory = messageFactory or UtilsFactory().createMessageFactory()
        self.widgetFactory = widgetFactory or WidgetFactory()
        self.functionsSettings = functionsSettings or FunctionsSettingsSingleton.getInstance()
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
        self.mStyleProfiles = None
        self.menuBarActions = []
        self.createActionsMenuBar()
        self.createMenuBar() 
        self.qgis.on('ReadProject', self.removeDockSap)
        self.qgis.on('NewProject', self.removeDockSap)

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

    def _executeCrud(self, widgetName, sapMethod, refreshMethod, data):
        try:
            message = sapMethod(data)
            self.showInfoMessageBox(None, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(None, 'Aviso', str(e))

    def createMenuBar(self):
        self.menuBarMain = self.qgis.addMenuBar('SAP Gerente')
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
        self.dockSap = self.widgetFactory.create(
            'DockSap', 
            self, 
            self.qgis,
            self.sapCtrl,
            self.fmeCtrl
        )
        self.qgis.addDockWidget(self.dockSap)
        self.disableMenuBar(False)

    def removeDockSap(self):
        self.qgis.removeDockWidget(self.dockSap) if self.dockSap else ''

    def disableMenuBar(self, b):
        self.menuBarMain.setDisabled(b)

    def getValuesFromLayer(self, functionName, fieldName, raiseOnError=False):
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
            if raiseOnError:
                raise
            self.dockSap.showError('Aviso', str(e))
            return ''

    def createWorkUnit(self, layerName, size, overlay, deplace, onlySelected):
        self.qgis.generateWorkUnit(
            layerName, size, overlay, deplace, onlySelected
        )

    def createWorkUnitSimple(self, data):
        if data['onlySelected']:
            extractSelectedFeatures = self.processingFactoryDsgTools.createProcessing('ExtractSelectedFeatures')
            result = extractSelectedFeatures.run(data)
            data['layer'] = result['OUTPUT']
        splitPolygons = self.processingFactoryDsgTools.createProcessing('SplitPolygons')
        result = splitPolygons.run(data)

        temporaryLayer = self.qgis.generateWorkUnitSimple(
            result['OUTPUT'], 
            data['epsg'], 
            data['bloco_id'], 
            data['dado_producao_id']
        )
        deaggregator = self.processingFactoryDsgTools.createProcessing('Deaggregator')
        deaggregator.run({'layerId': temporaryLayer.id()})
        return temporaryLayer


    def applyStylesOnLayers(self, stylesData):
        self.qgis.applyStylesOnLayers(stylesData)

    def createSapStyles(self, data):
        message = self.sapCtrl.createStyles(data)

    def updateSapStyles(self, data):
        self._executeCrud('MStyles', self.sapCtrl.updateStyles, self.sapCtrl.getStyles, data)

    def deleteSapStyles(self, data):
        self._executeCrud('MStyles', self.sapCtrl.deleteStyles, self.sapCtrl.getStyles, data)

    def getSapModels(self):
        try:
            return self.sapCtrl.getModels()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def addModel(self):
        mModels = self.widgetFactory.create('MModels', self)
        addModelForm = self.widgetFactory.create('AddModelForm', mModels)
        if not addModelForm.exec():
            return
        inputModelData = addModelForm.getData()
        self.createSapModels([inputModelData])

    def createSapModels(self, data):
        self._executeCrud('MModels', self.sapCtrl.createModels, self.getSapModels, data)

    def updateSapModels(self, data):
        self._executeCrud('MModels', self.sapCtrl.updateModels, self.getSapModels, data)

    def deleteSapModels(self, ids):
        self._executeCrud('MModels', self.sapCtrl.deleteModels, self.getSapModels, ids)

    def getSapRules(self, parent=None):
        try:
            return self.sapCtrl.getRules()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def getSapRuleSet(self, parent=None):
        return self.sapCtrl.getRuleSet()

    def getQgisLineEditExpression(self):
        return self.qgis.getWidgetByName('lineEditExpression')

    def openMRuleSet(self):
        mRules = self.widgetFactory.create('MRules', self)
        mRuleSet = self.widgetFactory.create('MRuleSet', self, mRules)
        mRuleSet.addRows(
            self.getSapRuleSet()
        )
        mRuleSet.exec()

    def addRuleSet(self):
        mRules = self.widgetFactory.create('MRules', self)
        mRuleSet = self.widgetFactory.create('MRuleSet', self, mRules)
        addRuleSetForm = self.widgetFactory.create(
            'AddRuleSetForm',
            parent=mRuleSet
        )
        if not addRuleSetForm.exec():
            return
        inputRuleSetData = addRuleSetForm.getData()
        self.createSapRuleSet([inputRuleSetData])

    def createSapRuleSet(self, data):
        self._executeCrud('MRuleSet', self.sapCtrl.createRuleSet, self.getSapRuleSet, data)

    def updateSapRuleSet(self, data):
        self._executeCrud('MRuleSet', self.sapCtrl.updateRuleSet, self.getSapRuleSet, data)

    def deleteSapRuleSet(self, ids):
        self._executeCrud('MRuleSet', self.sapCtrl.deleteRuleSet, self.getSapRuleSet, ids)
    
    def importRulesCsv(self):
        mRules = self.widgetFactory.create('MRules', self)
        addRulesCsvForm = self.widgetFactory.create('AddRulesCsvForm', self, parent=mRules)
        if not addRulesCsvForm.exec():
            return
        currentGroupRules = [ d['grupo_regra'].lower() for d in mRules.getGroupData()]
        rules = self.widgetFactory.create('Rules')
        newRules = rules.getRulesFromCsv(addRulesCsvForm.getData()['pathRulesCsv'])
        for groupRule in newRules:
            if not ( groupRule.lower() in currentGroupRules):
                groupData = mRules.getGroupData()
                groupData.append({
                    'grupo_regra' : groupRule,
                    'cor_rgb' : newRules[groupRule]['cor_rgb'],
                    'ordem' : newRules[groupRule]['ordem']
                })
                mRules.setGroupData(groupData)
            for ruleData in newRules[groupRule]['regras']:
                mRules.addRow(
                    '', 
                    groupRule, 
                    ruleData['schema'], 
                    ruleData['camada'],
                    ruleData['atributo'], 
                    ruleData['regra'], 
                    ruleData['descricao'],
                    self.getQgisLineEditExpression()
                )
        self.showInfoMessageBox(mRules, 'Aviso', 'Regras carregadas!')

    def downloadCsvRulesTemplate(self, destPath):
        rules = self.widgetFactory.create('Rules')
        rules.saveTemplateCsv(destPath)
    
    def loadLayersQgisProject(self, projectInProgress, block, lotInProgress):
        layersData = self.sapCtrl.getLayersQgisProject(projectInProgress, block, lotInProgress)

        if not layersData['views']:
            self.showInfoMessageBox(self.dockSap, 'Aviso', 'Sem views!')
            return
        
        dbName = layersData['banco_dados']['nome_db']
        dbHost = layersData['banco_dados']['servidor']
        dbPort = layersData['banco_dados']['porta']
        dbUser = layersData['banco_dados']['login']
        dbPassword = layersData['banco_dados']['senha']

        # SAP 3.0: as views são `lote_<L>_linha_<P>` (tipo 'lote') e
        # `lote_<L>_subfase_<S>` (tipo 'subfase'), com L o id do lote do acervo, e
        # cada uma já traz `lote` e `projeto` pelo nome. A subfase e a linha saem
        # pelo nome que o id no fim da view aponta.
        subphaseNames = {
            s['subfase_id']: s['subfase'] for s in self.sapCtrl.getSubphases()
        }
        lineNames = {
            l['linha_producao_id']: l['linha_producao'] for l in self.sapCtrl.getProductionLines()
        }

        groupBase = self.qgis.addLayerGroup('Acompanhamento')
        groupBlock = self.qgis.addLayerGroup('Bloco', groupBase)
        groupLote = self.qgis.addLayerGroup('Lote', groupBase) if not block else ''
        groupSubfase = self.qgis.addLayerGroup('Subfase', groupBase)

        layout = {
            'bloco': {
                'group': groupBlock,
                'blocos': []
            },
            'lote': {
                'group': groupLote,
                'projetos': {}
            },
            'subfase': {
                'group': groupSubfase,
                'projetos': {}
            }
        }

        #FORMATAR
        for viewData in layersData['views']:
            loteName = None
            groupName = viewData['tipo']

            if groupName == 'bloco':
                layout[groupName]['blocos'].append([
                    dbName, 
                    dbHost, 
                    dbPort, 
                    dbUser, 
                    dbPassword, 
                    viewData['schema'], 
                    viewData['nome'], 
                    'bloco'
                ])
                continue
          
            projectName = viewData['projeto']
            loteName = viewData['lote']
            idNoFim = int(viewData['nome'].split('_')[-1])

            if groupName == 'lote':

                if not( projectName in layout[groupName]['projetos']):
                    layout[groupName]['projetos'][projectName] = []

                # um lote do acervo atravessa linhas: uma view por linha
                layout[groupName]['projetos'][projectName].append([
                    dbName,
                    dbHost,
                    dbPort,
                    dbUser,
                    dbPassword,
                    viewData['schema'],
                    viewData['nome'],
                    '{0} - {1}'.format(loteName, lineNames.get(idNoFim, idNoFim))
                ])
            else:

                if idNoFim not in subphaseNames:
                    continue
                layerName = subphaseNames[idNoFim]

                if not( projectName in layout[groupName]['projetos']):
                    layout[groupName]['projetos'][projectName] = {}

                if not( loteName in layout[groupName]['projetos'][projectName] ):
                    layout[groupName]['projetos'][projectName][loteName] = []

                layout[groupName]['projetos'][projectName][loteName].append([
                    dbName, 
                    dbHost, 
                    dbPort, 
                    dbUser, 
                    dbPassword, 
                    viewData['schema'], 
                    viewData['nome'], 
                    layerName
                ])

        #CARREGAR CAMADAS
        for layer in layout['bloco']['blocos']:
            layer.append(groupBlock)
            blockMapLayer = self.qgis.loadLayer(*layer)
            if block:
                blockMapLayer.setSubsetString('"id" = {}'.format(block['id']))
            else:
                # SAP 3.0: o status do bloco é dominio.tipo_status_execucao, e
                # "em andamento" é não encerrado.
                blockMapLayer.setSubsetString("bloco_status NOT IN ('Concluído', 'Concluído parcialmente')")

        if not block:
            for project in layout['lote']['projetos']:
                group = self.qgis.addLayerGroup(project, groupLote)
                for layer in layout['lote']['projetos'][project]:
                    layer.append(group)
                    self.qgis.loadLayer(*layer)

        for project in layout['subfase']['projetos']:
            group = self.qgis.addLayerGroup(project, groupSubfase)
            
            for lote in layout['subfase']['projetos'][project]:
                
                groupLote = self.qgis.addLayerGroup(lote, group)
                groupLote.setIsMutuallyExclusive(True)

                for layer in sorted(layout['subfase']['projetos'][project][lote], key=lambda item: int(item[6].split('_')[-1])):
                    layer.append(groupLote)
                    subphaseMapLayer = self.qgis.loadLayer(*layer)
                    subphaseMapLayer.setAutoRefreshInterval(10 * 1000)
                    iface.setActiveLayer(subphaseMapLayer)
                    iface.activeLayer().setAutoRefreshEnabled(True)
                    subphaseMapLayer.setSubsetString(""""bloco" = '{}'""".format(block['nome'])) if block else ''

        groupSubfase.removeChildrenGroupWithoutLayers()
                    
    def activeRemoveByClip(self):
        self.qgis.activeMapToolByToolName('removeByClip')

    def activeRemoveByIntersect(self):
        self.qgis.activeMapToolByToolName('removeByIntersect')

    def getSapLayers(self, parent=None):
        try:
            return self.sapCtrl.getLayers()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def importLayers(self, layersImported, parent=None):
        # Quem chama é o próprio diálogo "Importar Camadas", que se recarrega
        # depois. A fábrica de widgets não tem `MImportLayers` (devolvia None e
        # o import quebrava DEPOIS de gravar no servidor).
        try:
            message = self.sapCtrl.importLayers(layersImported)
            if message:
                self.showInfoMessageBox(parent, 'Aviso', message)
            return message
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return None

    def getLayersFromPostgres(self, dbData, parent=None):
        # SAP 3.0: `GET /producao/login` devolve só o login, sem a senha; a
        # conexão é a salva no QGIS (`conexoesPostgresSalvas`).
        try:
            postgres = self.databasesFactory.getDatabase('Postgresql')
            postgres.setConnection(
                dbData['database'], dbData['host'], dbData['port'],
                dbData['username'], dbData['password']
            )
            return postgres.getLayers()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def getLayersFromVersionamento(self, repoId, parent=None):
        # Base versionada (dado de produção tipo 4): as camadas são os datasets
        # do repositório no serviço, lidos pelo repasse do SAP, sem PostGIS.
        try:
            return [
                datasetParaCamada(nome)
                for nome in self.sapCtrl.getVersionamentoDatasets(repoId)
            ]
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def openMEditLayers(self):
        mEditLayers = self.widgetFactory.create('MEditLayers', self)
        if mEditLayers.isVisible():
            mEditLayers.toTopLevel()
            return
        mEditLayers.addRows(self.getSapLayers(parent=mEditLayers))
        mEditLayers.show()

    def updateLayers(self, layersData):
        mEditLayers = self.widgetFactory.create('MEditLayers', self)
        self.sapCtrl.updateLayers(layersData)
        mEditLayers.addRows(self.getSapLayers(parent=mEditLayers))

    def deleteLayers(self, deletedLayersIds):
        mEditLayers = self.widgetFactory.create('MEditLayers', self)
        self.sapCtrl.deleteLayers(deletedLayersIds)
        mEditLayers.addRows(self.getSapLayers(parent=mEditLayers))

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

    def openMFmeServers(self):
        mFmeServers = self.widgetFactory.create('MFmeServers', self)
        if mFmeServers.isVisible():
            mFmeServers.toTopLevel()
            return
        mFmeServers.addRows(self.getSapFmeServers())
        mFmeServers.show()

    def getSapFmeServers(self, parent=None):
        try:
            return self.sapCtrl.getFmeServers()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def createFmeServers(self, fmeServers):
        self._executeCrud('MFmeServers', self.sapCtrl.createFmeServers, self.getSapFmeServers, fmeServers)

    def deleteFmeServers(self, fmeServersIds):
        self._executeCrud('MFmeServers', self.sapCtrl.deleteFmeServers, self.getSapFmeServers, fmeServersIds)

    def updateFmeServers(self, fmeServers):
        self._executeCrud('MFmeServers', self.sapCtrl.updateFmeServers, self.getSapFmeServers, fmeServers)

    def openMFmeProfiles(self):
        mFmeProfiles = self.widgetFactory.create('MFmeProfiles', self)
        mFmeServers = self.widgetFactory.create('MFmeServers', self)
        mFmeProfiles.setFmeServers(self.getSapFmeServers(mFmeServers))
        mFmeProfiles.setSubphases(self.getSapSubphases())
        if mFmeProfiles.isVisible():
            mFmeProfiles.toTopLevel()
            return
        mFmeProfiles.addRows(self.getSapFmeProfiles())
        mFmeProfiles.show()

    def getSapSubphases(self):
        return self.sapCtrl.getSubphases()
    
    def getProductionLines(self):
        return self.sapCtrl.getProductionLines()

    def getActiveProductionLines(self):
        return self.sapCtrl.getActiveProductionLines()

    def getSapPhases(self):
        return self.sapCtrl.getPhases()

    def getSapFmeProfiles(self):
        return self.sapCtrl.getFmeProfiles()

    def getFmeRoutines(self, server):
        # A rota projeto/configuracao/gerenciador_fme devolve {id, url}. Nao ha
        # porta separada, e fmeCtrl.getRoutines recebe so a url.
        try:
            return self.fmeCtrl.getRoutines(server)
        except Exception as e:
            self.showErrorMessageBox(self.dockSap, 'Aviso', 'Erro ao buscar rotinas no servidor do FME. Verifique se o servidor está ativo.')
            return []

    def addFmeProfile(self):
        mFmeProfiles = self.widgetFactory.create('MFmeProfiles', self)
        addFmeProfileForm = self.widgetFactory.create('AddFmeProfileForm', self, mFmeProfiles)
        addFmeProfileForm.loadFmeServers(self.getSapFmeServers())
        addFmeProfileForm.loadSubphases(self.getSapSubphases())
        if not addFmeProfileForm.exec():
            return
        inputFmeProfileData = addFmeProfileForm.getData()
        self.createFmeProfiles([inputFmeProfileData])

    def createFmeProfiles(self, fmeProfiles):
        self._executeCrud('MFmeProfiles', self.sapCtrl.createFmeProfiles, self.getSapFmeProfiles, fmeProfiles)

    def deleteFmeProfiles(self, fmeProfilesIds):
        self._executeCrud('MFmeProfiles', self.sapCtrl.deleteFmeProfiles, self.getSapFmeProfiles, fmeProfilesIds)

    def updateFmeProfiles(self, fmeProfiles):
        self._executeCrud('MFmeProfiles', self.sapCtrl.updateFmeProfiles, self.getSapFmeProfiles, fmeProfiles)

    def getSapStepsByFeatureId(self, featureIdList):
        subphaseIdSet = set()
        for featureId in featureIdList:
            featid = self.qgis.getActiveLayerAttribute(featureId, 'subfase_id')
            subphaseIdSet.add(featid)
            if len(subphaseIdSet) > 1:
                break

        if len(subphaseIdSet) > 1:
            raise Exception("Verificar unidades de trabalho selecionadas para que a seleção contenha apenas uma subfase")
        featureId = featureIdList[0]
        subphaseId = self.qgis.getActiveLayerAttribute(featureId, 'subfase_id')
        loteId = self.qgis.getActiveLayerAttribute(featureId, 'lote_id')
        steps = self.getSapSteps()
        return [ 
            step for step in steps \
                if step['subfase_id'] == subphaseId and step['lote_id'] == loteId
        ]

    def getSapStepsByFieldName(self, featureId, fieldName):
        value = self.qgis.getActiveLayerAttribute(featureId, fieldName)
        steps = self.getSapSteps()
        return [ step for step in steps if step[fieldName] == value ]

    def getSapSteps(self):
        return self.sapCtrl.getSteps()

    def getSapStepsByTag(self, tag, withDuplicate=False, numberTag='', tagFilter=('', ''), sortByTag='', exactMatch=False):
        def defaultOrder(elem):
            return elem['ordem_fase']
        def atoi(text):
            return int(text) if text.isdigit() else text
        def orderBy(elem):
            return [ atoi(c) for c in re.split(r'(\d+)', elem[sortByTag].lower()) ]
        steps = self.sapCtrl.getSubphases()
        steps.sort(key=defaultOrder)
        if tagFilter[0] and tagFilter[1]:
            steps = [ s for s in steps if s[tagFilter[0]] == tagFilter[1]]
        selectedSteps = []
        for step in steps:
            value = step[tag]
            if exactMatch:
                tagTest = [ t[tag] for t in selectedSteps if str(value).lower() == str(t[tag]).lower() ]
            else:
                tagTest = [ t[tag] for t in selectedSteps if str(value).lower() in str(t[tag]).lower() ]
            if not(withDuplicate) and tagTest:
                continue
            if numberTag:
                number = len([ t for t in selectedSteps if str(step[numberTag]).lower() in str(t[numberTag]).lower() ]) + 1
                step[numberTag] = "{0} {1}".format(step[numberTag], number)
            selectedSteps.append(step)
        if sortByTag:
            selectedSteps.sort(key=orderBy)
        return selectedSteps

    def getQgisComboBoxPolygonLayer(self):
        return self.qgis.getWidgetByName('comboBoxPolygonLayer')

    def getQgisComboBoxProjection(self):
        return self.qgis.getWidgetByName('comboBoxProjection')

    def loadSapWorkUnits(self, layer, lotId, subphaseIds, onlySelected, associatedFields):
        features = self.qgis.dumpFeatures(layer, onlySelected)
        fieldsType = {
            'disponivel' : bool,
            'dado_producao_id' : int,
            'bloco_id' : int,
            'prioridade' : int,
            'dificuldade' : int,
            'tempo_estimado_minutos' : int
        }
        workUnits = []
        for feat in features:
            data = {}
            for field in associatedFields:
                value = str(feat[ associatedFields[field]])
                try:
                    data[field] = fieldsType[field](value) if field in fieldsType else value
                except Exception:
                    self.showErrorMessageBox(self.dockSap, 'Aviso', f'Tipo do campo ${field} inválido!')
                    return
            data['geom'] = self.qgis.geometryToEwkt( feat['geometry'], layer.crs().authid(), 'EPSG:4326' )
            if not self.qgis.isValidEpsg(data['epsg']):
                self.showErrorMessageBox(self.dockSap, 'Aviso', 'Há "EPSG" inválido!')
                return
            workUnits.append(data)
        invalidWorkUnits = [ 
            p for p in workUnits 
            if [
                True for k in p.keys()
                if p[k] is None
            ]
        ]
        if invalidWorkUnits:
            self.showErrorMessageBox(self.dockSap, 'Aviso', 'Há feições com dados nulo. Para carregar unidades de trabalho as feições só podem ter a observação nula.')
            return
        try:
            message = self.sapCtrl.loadWorkUnit(lotId, subphaseIds, workUnits)
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

    def getSapBlocks(self):
        return self.sapCtrl.getBlocks()

    def alterSapBlock(self, workspacesIds, blockId):
        self.sapCtrl.alterBlock(workspacesIds, blockId)

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
            activityData = self.sapCtrl.getNextActivityDataByUser(userId, nextActivity)
            if not activityData['dados']:
                raise Exception('Usuário sem atividades!')
            self.qgis.startSapFP(
                activityData
            )
            return True
        except Exception as e:
            self.showErrorMessageBox(None, 'Aviso', str(e))
            return False

    # Pausar, reiniciar e voltar devolvem o que mostrar: `{'texto', 'alerta'}`
    # com a mensagem do servidor e, quando vier, o resultado da revogação do
    # acesso (`alerta` quando ela falhou), ou False quando a chamada falhou e o
    # erro já foi mostrado por `checkError`.
    def _resultadoMaquinaEstado(self, resposta):
        if not resposta:
            return False
        return {
            'texto': mensagemComRevogacao(resposta),
            'alerta': revogacaoFalhou(resposta)
        }

    def pauseSapActivity(self, workspacesIds):
        return self._resultadoMaquinaEstado(self.sapCtrl.pauseActivity(workspacesIds))

    def resetSapPrivileges(self):
        return self.sapCtrl.resetPrivileges()

    def restartSapActivity(self, workspacesIds):
        return self._resultadoMaquinaEstado(self.sapCtrl.restartActivity(workspacesIds))

    def returnSapActivityToPreviousStep(self, activityIds, preserveUser):
        return self._resultadoMaquinaEstado(
            self.sapCtrl.returnActivityToPreviousStep(activityIds, preserveUser)
        )

    def revokeSapPrivileges(self, dadoProducaoId):
        self.sapCtrl.revokePrivileges(dadoProducaoId)

    def setSapPriorityActivity(self, activityIds, priority, userId):
        self.sapCtrl.setPriorityActivity(activityIds, priority, userId)

    def unlockSapWorkspace(self, workspacesIds):
        self.sapCtrl.unlockWorkspace(workspacesIds)
    
    def getSapDatabases(self):
        return self.sapCtrl.getDatabases()

    def getSapProductionData(self):
        return self.sapCtrl.getProductionData()

    def getSapInputGroups(self):
        return self.sapCtrl.getInputGroups()

    def getSapInsumos(self, grupoInsumoId=None, tipoInsumoCode=None):
        return self.sapCtrl.getInsumos(grupoInsumoId, tipoInsumoCode)

    def updateSapInsumos(self, insumos):
        self.sapCtrl.updateInsumos(insumos)

    def deleteSapInsumos(self, insumoIds):
        self.sapCtrl.deleteInsumos(insumoIds)

    def getSapInsumosPorUT(self, unidadeTrabalhoId):
        return self.sapCtrl.getInsumosPorUT(unidadeTrabalhoId)

    def getSapModelProfiles(self):
        try:
            return self.sapCtrl.getModelProfiles()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def updateSapModelProfiles(self, data):
        self._executeCrud('MModelProfiles', self.sapCtrl.updateModelProfiles, self.getSapModelProfiles, data)

    def deleteSapModelProfiles(self, ids):
        self._executeCrud('MModelProfiles', self.sapCtrl.deleteModelProfiles, self.getSapModelProfiles, ids)

    def openMRuleProfiles(self):
        mRuleProfiles = self.widgetFactory.create('MRuleProfiles', self)
        mRuleProfiles.setSubphases(self.getSapSubphases())
        mRuleProfiles.setRules(self.getSapRules())
        mRuleProfiles.setLots(self.getSapLots())
        if mRuleProfiles.isVisible():
            mRuleProfiles.toTopLevel()
            return
        mRuleProfiles.addRows(self.sapCtrl.getRuleProfiles())
        mRuleProfiles.show()

    def addRuleProfile(self):
        mRuleProfiles = self.widgetFactory.create('MRuleProfiles', self)
        addRuleProfileForm = self.widgetFactory.create('AddRuleProfileForm', mRuleProfiles)
        addRuleProfileForm.loadSubphases(self.getSapSubphases())
        addRuleProfileForm.loadRules(self.getSapRules())
        addRuleProfileForm.loadLots(self.getSapLots())
        if not addRuleProfileForm.exec():
            return
        inputRuleProfileData = addRuleProfileForm.getData()
        self.createSapRuleProfiles([inputRuleProfileData])
        mRuleProfiles.adjustColumns()

    def createSapRuleProfiles(self, data):
        self._executeCrud('MRuleProfiles', self.sapCtrl.createRuleProfiles, self.sapCtrl.getRuleProfiles, data)

    def updateSapRuleProfiles(self, data):
        self._executeCrud('MRuleProfiles', self.sapCtrl.updateRuleProfiles, self.sapCtrl.getRuleProfiles, data)

    def deleteSapRuleProfiles(self, ids):
        self._executeCrud('MRuleProfiles', self.sapCtrl.deleteRuleProfiles, self.sapCtrl.getRuleProfiles, ids)

    def getSapStyleNames(self):
        return self.sapCtrl.getGroupStyles()

    def createGroupStyles(self, data):
        self.sapCtrl.createGroupStyles(data)

    def getSapStyleProfiles(self):
        try:
            return self.sapCtrl.getStyleProfiles()
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return []

    def addStyleProfile(self):
        mStyleProfiles = self.widgetFactory.create('MStyleProfiles', self, self.qgis, self.sapCtrl)
        addStyleProfile = self.widgetFactory.create('AddStyleProfileForm', mStyleProfiles)
        addStyleProfile.loadSubphases(self.getSapSubphases())
        addStyleProfile.loadGroupStyles(self.sapCtrl.getGroupStyles())
        addStyleProfile.loadLots(self.getSapLots())
        if not addStyleProfile.exec():
            return
        inputStyleProfileData = addStyleProfile.getData()
        self.createSapStyleProfiles([inputStyleProfileData])
        mStyleProfiles.adjustColumns()

    def createSapStyleProfiles(self, data):
        self._executeCrud('MStyleProfiles', self.sapCtrl.createStyleProfiles, self.getSapStyleProfiles, data)

    def updateSapStyleProfiles(self, data):
        self._executeCrud('MStyleProfiles', self.sapCtrl.updateStyleProfiles, self.getSapStyleProfiles, data)

    def deleteSapStyleProfiles(self, ids):
        self._executeCrud('MStyleProfiles', self.sapCtrl.deleteStyleProfiles, self.getSapStyleProfiles, ids)

    def getScreenLayers(self, functionName, fieldName):
        selectedlayers = self.qgis.getSelectedLayersTreeView()
        layerSettings = self.functionsSettings.getSettings(functionName, fieldName)
        values = []
        try:
            for layer in selectedlayers:
                tableName = layer.dataProvider().uri().table()
                for layerOptions in layerSettings:
                    if ( 
                            layerOptions['layerName'] != '*' and 
                            not( layerOptions['layerName'] in tableName ) 
                        ):
                        continue
                    values.append( tableName )
                    break
            return ",".join([ name for name in values ])
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return ''    

    def createScreens(self, primaryLayerNames, secundaryLayerNames):
        self.qgis.createScreens( primaryLayerNames, secundaryLayerNames )

    def getSapProjects(self):
        return self.sapCtrl.getProjects()

    def openAssociateUserToProfiles(self, parent):
        if self.assocUserToProfDlg and not sip.isdeleted(self.assocUserToProfDlg):
            self.assocUserToProfDlg.close()
        self.assocUserToProfDlg = self.widgetFactory.create('AssociateUserToProfiles', self, parent)
        self.assocUserToProfDlg.setUsers( self.sapCtrl.getActiveUsers() )
        self.assocUserToProfDlg.setProfiles( self.getSapProductionProfiles() )
        self.assocUserToProfDlg.updateTable()
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
        self.addProfProdDlg.save.connect(callback)
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
        self.aProfProdRelDlg.loadProductionLines( self.getActiveProductionLines() )
        self.aProfProdRelDlg.loadSubphases( [] )
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
        self.aProfProdRelDlg.loadProductionLines( self.getActiveProductionLines() )
        self.aProfProdRelDlg.loadSubphases( self.getSapSubphases() )
        self.aProfProdRelDlg.loadSteps( self.getSapStepType() )
        self.aProfProdRelDlg.activeEditMode(True)
        self.aProfProdRelDlg.setCurrentId(data['id'])
        self.aProfProdRelDlg.setData(data)
        self.aProfProdRelDlg.save.connect(callback)
        self.aProfProdRelDlg.show()

    def getSapStepType(self):
        return self.sapCtrl.getStepType()

    def getSapQualityControlTypes(self):
        return self.sapCtrl.getQualityControlTypes()

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
        self.sapCtrl.createProductionProfiles(data)

    def updateSapProductionProfiles(self, data):
        self.sapCtrl.updateProductionProfiles(data)

    def deleteSapProductionProfiles(self, data, parent):
        self.sapCtrl.deleteProductionProfiles(data)

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
            profile = next((p for p in profiles if p['id'] == d['habilitacao_id']), None)
            if profile:
                d['habilitacao'] = profile['nome']
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

    def createAllActivities(self, lotId):
        return self.sapCtrl.createAllActivities(lotId)

    def createDefaultStep(self, padraoCq, phaseId, lotId):
        return self.sapCtrl.createDefaultStep(padraoCq, phaseId, lotId)
    
    def deleteSAPUTWithoutActivity(self):
        self.sapCtrl.deleteUTWithoutActivity()
