from Ferramentas_Gerencia.widgets.advanceActivityToNextStep  import AdvanceActivityToNextStep
from Ferramentas_Gerencia.widgets.createPriorityGroupActivity  import CreatePriorityGroupActivity
from Ferramentas_Gerencia.widgets.openNextActivityByUser  import OpenNextActivityByUser
from Ferramentas_Gerencia.widgets.fillComments  import FillComments
from Ferramentas_Gerencia.widgets.openActivity  import OpenActivity
from Ferramentas_Gerencia.widgets.lockWorkspace  import LockWorkspace
from Ferramentas_Gerencia.widgets.pauseActivity  import PauseActivity
from Ferramentas_Gerencia.widgets.unlockWorkspace  import UnlockWorkspace
from Ferramentas_Gerencia.widgets.restartActivity  import RestartActivity
from Ferramentas_Gerencia.widgets.setPriorityActivity  import SetPriorityActivity
from Ferramentas_Gerencia.widgets.returnActivityToPreviousStep  import ReturnActivityToPreviousStep
from Ferramentas_Gerencia.widgets.mStyles  import MStyles
from Ferramentas_Gerencia.widgets.mModels  import MModels
from Ferramentas_Gerencia.widgets.mRules  import MRules
from Ferramentas_Gerencia.widgets.generatesWorkUnit  import GeneratesWorkUnit
from Ferramentas_Gerencia.widgets.generatesWorkUnitSimple  import GeneratesWorkUnitSimple
from Ferramentas_Gerencia.widgets.updateBlockedActivities  import UpdateBlockedActivities
from Ferramentas_Gerencia.widgets.downloadQgisProject  import DownloadQgisProject
from Ferramentas_Gerencia.widgets.loadLayersQgisProject  import LoadLayersQgisProject
from Ferramentas_Gerencia.widgets.deleteFeatures  import DeleteFeatures
from Ferramentas_Gerencia.widgets.synchronizeUserInformation  import SynchronizeUserInformation
from Ferramentas_Gerencia.widgets.importUsersAuthServiceDlg  import ImportUsersAuthServiceDlg
from Ferramentas_Gerencia.widgets.mUsersPrivileges  import MUsersPrivileges
from Ferramentas_Gerencia.widgets.deleteActivities  import DeleteActivities
from Ferramentas_Gerencia.widgets.createActivities  import CreateActivities
from Ferramentas_Gerencia.widgets.resetPrivileges  import ResetPrivileges
from Ferramentas_Gerencia.widgets.revokePrivileges  import RevokePrivileges
from Ferramentas_Gerencia.widgets.mEditLayers  import MEditLayers
from Ferramentas_Gerencia.widgets.mImportLayers  import MImportLayers
from Ferramentas_Gerencia.widgets.alterBlock  import AlterBlock
from Ferramentas_Gerencia.widgets.copySetupToLocalMode  import CopySetupToLocalMode
from Ferramentas_Gerencia.widgets.createScreens  import CreateScreens
from Ferramentas_Gerencia.widgets.mFmeServers  import MFmeServers
from Ferramentas_Gerencia.widgets.mFmeProfiles  import MFmeProfiles
from Ferramentas_Gerencia.widgets.clearUserActivities  import ClearUserActivities
from Ferramentas_Gerencia.widgets.deleteAssociatedInputs  import DeleteAssociatedInputs
from Ferramentas_Gerencia.widgets.associateInputs  import AssociateInputs
from Ferramentas_Gerencia.widgets.deleteWorkUnits  import DeleteWorkUnits
from Ferramentas_Gerencia.widgets.createProduct  import CreateProduct
from Ferramentas_Gerencia.widgets.loadWorkUnit  import LoadWorkUnit
from Ferramentas_Gerencia.widgets.copyWorkUnit  import CopyWorkUnit
from Ferramentas_Gerencia.widgets.mModelProfiles  import MModelProfiles
from Ferramentas_Gerencia.widgets.mRuleProfiles  import MRuleProfiles
from Ferramentas_Gerencia.widgets.mStyleProfiles  import MStyleProfiles
from Ferramentas_Gerencia.widgets.associateUserToBlocks import AssociateUserToBlocks
from Ferramentas_Gerencia.widgets.associateUserToProfiles import AssociateUserToProfiles
from Ferramentas_Gerencia.widgets.mStyleGroups import MStyleGroups
from Ferramentas_Gerencia.widgets.mMenu  import MMenu
from Ferramentas_Gerencia.widgets.mMenuProfile  import MMenuProfile
from Ferramentas_Gerencia.widgets.mInputGroup  import MInputGroup
from Ferramentas_Gerencia.widgets.createInputs  import CreateInputs
from Ferramentas_Gerencia.widgets.createAllActivities  import CreateAllActivities
from Ferramentas_Gerencia.widgets.createDefaultSteps  import CreateDefaultSteps
from Ferramentas_Gerencia.widgets.profileProductionSetting import ProfileProductionSetting
from Ferramentas_Gerencia.widgets.deleteWorkUnitActivities import DeleteWorkUnitActivities
from Ferramentas_Gerencia.widgets.updateLayersQgisProject import UpdateLayersQgisProject
from Ferramentas_Gerencia.widgets.mProjects  import MProjects
from Ferramentas_Gerencia.widgets.mLots  import MLots
from Ferramentas_Gerencia.widgets.mBlocks  import MBlocks
from Ferramentas_Gerencia.widgets.mProductionData  import MProductionData
from Ferramentas_Gerencia.widgets.associateBlockInputs  import AssociateBlockInputs
from Ferramentas_Gerencia.widgets.revokeUserPrivileges  import RevokeUserPrivileges
from Ferramentas_Gerencia.widgets.setQgisVersion  import SetQgisVersion
from Ferramentas_Gerencia.widgets.mProfileFinalization  import MProfileFinalization
from Ferramentas_Gerencia.widgets.mAlias  import MAlias
from Ferramentas_Gerencia.widgets.mAliasProfile  import MAliasProfile
from Ferramentas_Gerencia.widgets.mPlugin  import MPlugin
from Ferramentas_Gerencia.widgets.mShortcut  import MShortcut
from Ferramentas_Gerencia.widgets.mLineage  import MLineage
from Ferramentas_Gerencia.widgets.mProblemActivity  import MProblemActivity
from Ferramentas_Gerencia.widgets.mThemes  import MThemes
from Ferramentas_Gerencia.widgets.mThemesProfile import MThemesProfile
from Ferramentas_Gerencia.widgets.mLastCompletedActivities import MLastCompletedActivities
from Ferramentas_Gerencia.widgets.mRunningActivities import MRunningActivities
from Ferramentas_Gerencia.widgets.reshapeUT import ReshapeUT
from Ferramentas_Gerencia.widgets.cutUT import CutUT
from Ferramentas_Gerencia.widgets.mergeUT import MergeUT
from Ferramentas_Gerencia.widgets.setupSAPLocal import SetupSAPLocal
from Ferramentas_Gerencia.widgets.endSAPLocal import EndSAPLocal
from Ferramentas_Gerencia.widgets.mChangeReport import MChangeReport
from Ferramentas_Gerencia.widgets.resetEstimatedTimeAndDifficulty import ResetEstimatedTimeAndDifficulty
from Ferramentas_Gerencia.widgets.setRepositoryPluginURL import SetRepositoryPluginURL
from Ferramentas_Gerencia.widgets.addProductionLine import AddProductionLine

class DockDirector:

    #interface
    def constructSapMDock(self, dockSapBuilder, controller, qgis, sap, fme):
        users = sap.getActiveUsers()
        databases = controller.getSapDatabases()
        instance = None #dockSapBuilder.getInstance()
        dockSapBuilder.setController(controller)
        #management project tab
        for functionWidget in [
                {
                    "name" : 'Carregar Camadas de Acompanhamento',
                    "widget" : lambda: LoadLayersQgisProject(controller, sap)
                },
                {
                    "name" : 'Problemas Reportados',
                    "widget" : lambda: MProblemActivity(controller, qgis, sap)
                },
                {
                    "name" : 'Abrir Atividade',
                    "widget" : lambda: OpenActivity(controller)
                },
                {
                    "name" : 'Abrir Atividade do Operador',
                    "widget" : lambda: OpenNextActivityByUser(users, controller)
                },
                {
                    "name" : 'Bloquear Unidades de Trabalho',
                    "widget" : lambda: LockWorkspace(controller)
                },
                {
                    "name" : 'Desbloquear Unidades de Trabalho',
                    "widget" : lambda: UnlockWorkspace(controller)
                },
                {
                    "name" : 'Alterar Bloco de Unidade de Trabalho',
                    "widget" : lambda: AlterBlock(controller)
                },
                {
                    "name" : 'Pausar Atividades em Execução',
                    "widget" : lambda: PauseActivity(controller)
                },
                {
                    "name" : 'Reiniciar Atividades em Execução ou Pausadas',
                    "widget" : lambda: RestartActivity(controller)
                },
                {
                    "name" : 'Definir Atividades Prioritárias',
                    "widget" : lambda: SetPriorityActivity(controller, qgis, sap)
                },
                {
                    "name" : 'Definir Atividades Prioritárias de Grupo',
                    "widget" : lambda: CreatePriorityGroupActivity(controller, qgis, sap)
                },
                {
                    "name" : 'Avançar Atividades para Próxima Etapa',
                    "widget" : lambda: AdvanceActivityToNextStep(controller)
                },
                {
                    "name" : 'Retornar Atividades para Etapa Anterior',
                    "widget" : lambda: ReturnActivityToPreviousStep(controller)
                },
                {
                    "name" : 'Preencher Observações',
                    "widget" : lambda: FillComments(controller)
                },
                {
                    "name" : 'Atualizar Camadas de Acompanhamento',
                    "widget" : lambda: UpdateLayersQgisProject(controller, sap)
                },
                {
                    "name" : 'Criar Telas de Acompanhamento',
                    "widget" : lambda: CreateScreens(controller)
                },
                {
                    "name" : 'Redefinir Permissões',
                    "widget" : lambda: ResetPrivileges(controller)
                },
                {
                    "name" : 'Revogar Permissões',
                    "widget" : lambda: RevokePrivileges(databases, controller)
                },
                {
                    "name" : 'Revogar Permissões Usuários',
                    "widget" : lambda: RevokeUserPrivileges(databases, controller, sap)
                },
                # {
                #     "name" : 'Copiar configurações para Modo Local',
                #     "widget" : lambda: CopySetupToLocalMode(databases, controller)
                # },
                {
                    "name" : 'Definir Versão Mínima do QGIS',
                    "widget" : lambda: SetQgisVersion(sap)
                },
                {
                    "name": "Configurar Atualizador de Plugins",
                    "widget": lambda: SetRepositoryPluginURL(sap)
                },
                {
                    "name" : 'Gerenciador Plugins',
                    "widget" : lambda: MPlugin(controller, qgis, sap)
                },
                {
                    "name" : 'Gerenciador Atalhos',
                    "widget" : lambda: MShortcut(controller, qgis, sap)
                },
                {
                    "name" : 'Reshape Unidade de Trabalho',
                    "widget" : lambda: ReshapeUT(controller, qgis, sap)
                },
                {
                    "name" : 'Corta Unidade de Trabalho',
                    "widget" : lambda: CutUT(controller, qgis, sap)
                },
                {
                    "name" : 'Merge Unidade de Trabalho',
                    "widget" : lambda: MergeUT(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar SAP Local',
                    "widget" : lambda: SetupSAPLocal(users, controller, qgis, sap)
                },
                {
                    "name" : 'Finalizar SAP Local',
                    "widget" : lambda: EndSAPLocal(controller, qgis, sap)
                },
                {
                    'name': 'Relatório de Alterações',
                    'widget': lambda: MChangeReport(controller, qgis, sap)
                },
                {
                    'name': 'Redefinir tempo estimado e dificuldade',
                    'widget': lambda: ResetEstimatedTimeAndDifficulty(controller, qgis, sap)
                }
            ]:
            dockSapBuilder.addProjectManagementWidget(functionWidget['name'], functionWidget['widget'])
        #creation project tab
        for functionWidget in [
                {
                    "name" : 'Criar Projeto',
                    "widget" : lambda: MProjects(controller, qgis, sap)
                },
                # {
                #     "name" : 'Atividades em execução',
                #     "widget" : lambda: MRunningActivities(controller, qgis, sap)
                # },
                # {
                #     "name" : 'Últimas atividades finalizadas',
                #     "widget" : lambda: MLastCompletedActivities(controller, qgis, sap)
                # },
                {
                    "name" : 'Configurar perfil de Linhagem',
                    "widget" : lambda: MLineage(controller, qgis, sap)
                },
                {
                    "name" : 'Criar Lote',
                    "widget" : lambda: MLots(controller, qgis, sap)
                },
                {
                    "name" : 'Carregar Produtos',
                    "widget" : lambda: CreateProduct(
                        controller.getQgisComboBoxPolygonLayer(), 
                        controller.getQgisComboBoxPolygonLayer(),
                        controller,
                        qgis
                    )
                },
                {
                    "name" : 'Criar Bloco',
                    "widget" : lambda: MBlocks(controller, qgis, sap)
                },
                {
                    "name" : 'Criar Etapas Padrão',
                    "widget" : lambda: CreateDefaultSteps(controller)
                },
                {
                    "name" : 'Configurações de Conexão',
                    "widget" : lambda: MProductionData(controller, qgis, sap)
                },
                {
                    "name" : 'Gerar Unidades de Trabalho',
                    "widget" : lambda: GeneratesWorkUnitSimple(
                        controller.getQgisComboBoxPolygonLayer(), 
                        controller.getQgisComboBoxProjection(),
                        controller,
                        sap,
                        qgis
                    )
                },
                {
                    "name" : 'Gerar Unidades de Trabalho Avançado',
                    "widget" : lambda: GeneratesWorkUnit(
                        controller.getQgisComboBoxPolygonLayer(), 
                        controller.getQgisComboBoxProjection(),
                        controller,
                        sap,
                        qgis
                    )
                },
                {
                    "name" : 'Carregar Unidades de Trabalho',
                    "widget" : lambda: LoadWorkUnit(controller.getQgisComboBoxPolygonLayer(), controller)
                },
                {
                    "name" : 'Copiar Unidades de Trabalho',
                    "widget" : lambda: CopyWorkUnit(controller)
                },
                {
                    "name" : 'Deletar Unidades de Trabalho',
                    "widget" : lambda: DeleteWorkUnits(controller)
                },
                {
                    "name" : 'Criar Todas as Atividades',
                    "widget" : lambda: CreateAllActivities(controller, sap)
                },
                {
                    "name" : 'Criar Atividades',
                    "widget" : lambda: CreateActivities(controller, qgis, sap)
                },
                {
                    "name" : 'Deletar Atividades Não Iniciadas',
                    "widget" : lambda: DeleteActivities(controller)
                },
                {
                    "name" : 'Deletar Atividades de Unidade de Trabalho',
                    "widget" : lambda: DeleteWorkUnitActivities(controller, sap)
                },
                {
                    "name": 'Configurar Grupo de Insumos',
                    "widget": lambda: MInputGroup(controller, qgis, sap)
                },
                {
                    "name": 'Carregar Metadado dos Insumos',
                    "widget": lambda: CreateInputs(controller, qgis, sap)
                },
                {
                    "name" : 'Associar Insumos a Unidades de Trabalho',
                    "widget" : lambda: AssociateInputs(controller.getSapInputGroups(), controller)
                },
                {
                    "name" : 'Associar Insumos ao Bloco',
                    "widget" : lambda: AssociateBlockInputs(controller.getSapInputGroups(), controller, qgis, sap)
                },
                {
                    "name" : 'Deletar Insumos Associados',
                    "widget" : lambda: DeleteAssociatedInputs(controller.getSapInputGroups(), controller)
                },
                {
                    "name" : 'Importar Usuários',
                    "widget" : lambda: ImportUsersAuthServiceDlg(controller, qgis, sap)
                },
                {
                    "name" : 'Sincronizar Informações de Usuários',
                    "widget" : lambda: SynchronizeUserInformation(controller)
                },
                {
                    "name" : 'Modificar Permissões de Usuários',
                    "widget" : lambda: MUsersPrivileges(controller, qgis, sap)
                },
                {
                    "name": 'Gerenciar Perfis de Produção',
                    "widget": lambda: ProfileProductionSetting(
                        controller, qgis, sap,
                        parent=instance
                    )
                },
                                {
                    "name": 'Associar Usuários à Perfis de Produção',
                    "widget": lambda: AssociateUserToProfiles(
                        controller, qgis, sap,
                        parent=instance
                    )
                },
                {
                    "name": 'Associar Usuários à Blocos',
                    "widget": lambda: AssociateUserToBlocks(
                        controller, qgis, sap,
                        parent=instance
                    )
                },
                {
                    "name" : 'Gerenciador Grupo de Estilos',
                    "widget" : lambda: MStyleGroups(controller, qgis, sap)
                },
                {
                    "name" : 'Gerenciador de Estilos',
                    "widget" : lambda: MStyles(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar Perfis de Estilos',
                    "widget" : lambda: MStyleProfiles(controller, qgis, sap)
                },
                {
                    "name" : 'Gerenciador de Modelos',
                    "widget" : lambda: MModels(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar Perfis de Modelos',
                    "widget" : lambda: MModelProfiles(controller, qgis, sap)
                },
                {
                    "name" : 'Gerenciador de Regras',
                    "widget" : lambda: MRules(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar Perfis de Regras',
                    "widget" : lambda: MRuleProfiles(controller, qgis, sap)
                },
                {
                    "name": 'Gerenciador de Menus',
                    "widget": lambda: MMenu(controller, qgis, sap)
                },
                {
                    "name": 'Configurar Perfis de Menu',
                    "widget": lambda: MMenuProfile(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar Servidores do Gerenciador FME',
                    "widget" : lambda: MFmeServers(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar Perfil de Rotinas FME',
                    "widget" : lambda: MFmeProfiles(controller, qgis, sap, fme)
                },
                {
                    "name": 'Gerenciador de Perfil Finalização',
                    "widget": lambda: MProfileFinalization(
                        controller, qgis, sap,
                        parent=instance
                    )
                },
                {
                    "name" : 'Gerenciador de Alias',
                    "widget" : lambda: MAlias(controller, qgis, sap)
                },
                {
                    "name" : 'Gerenciador de Perfil Alias',
                    "widget" : lambda: MAliasProfile(controller, qgis, sap)
                },
                {
                    "name": 'Gerenciador de Temas',
                    "widget": lambda: MThemes(controller, qgis, sap)
                },
                {
                    "name": 'Gerenciador Perfis de Temas',
                    "widget": lambda: MThemesProfile(controller, qgis, sap)
                }
            ]:
            dockSapBuilder.addProjectCreationWidget(functionWidget['name'], functionWidget['widget'])
        #danger zone tab
        
        for functionWidget in [
                {
                    "name" : 'Gerar Projeto de Acompanhamento',
                    "widget" : lambda: DownloadQgisProject(controller)
                },
                {
                    "name" : 'Remover Feições em Área',
                    "widget" : lambda: DeleteFeatures(controller)
                },
                {
                    "name" : 'Limpar Atividades de Usuário',
                    "widget" : lambda: ClearUserActivities(users, controller)
                },
                {
                    "name" : 'Importar Camadas',
                    "widget" : lambda: MImportLayers(controller)
                },
                {
                    "name" : 'Configurar Camadas',
                    "widget" : lambda: MEditLayers(controller, qgis, sap)
                },
                {
                    "name" : 'Adicionar Linha de Producao',
                    "widget" : lambda: AddProductionLine(controller, qgis, sap)
                }
            ]:
            dockSapBuilder.addDangerZoneWidget(functionWidget['name'], functionWidget['widget'])
            
            
