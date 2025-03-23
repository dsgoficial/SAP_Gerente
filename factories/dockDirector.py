from SAP_Gerente.widgets.advanceActivityToNextStep  import AdvanceActivityToNextStep
from SAP_Gerente.widgets.createPriorityGroupActivity  import CreatePriorityGroupActivity
from SAP_Gerente.widgets.openNextActivityByUser  import OpenNextActivityByUser
from SAP_Gerente.widgets.fillComments  import FillComments
from SAP_Gerente.widgets.openActivity  import OpenActivity
from SAP_Gerente.widgets.lockWorkspace  import LockWorkspace
from SAP_Gerente.widgets.pauseActivity  import PauseActivity
from SAP_Gerente.widgets.unlockWorkspace  import UnlockWorkspace
from SAP_Gerente.widgets.restartActivity  import RestartActivity
from SAP_Gerente.widgets.setPriorityActivity  import SetPriorityActivity
from SAP_Gerente.widgets.returnActivityToPreviousStep  import ReturnActivityToPreviousStep
from SAP_Gerente.widgets.mStyles  import MStyles
from SAP_Gerente.widgets.mModels  import MModels
from SAP_Gerente.widgets.mRules  import MRules
from SAP_Gerente.widgets.generatesWorkUnit  import GeneratesWorkUnit
from SAP_Gerente.widgets.generatesWorkUnitSimple  import GeneratesWorkUnitSimple
from SAP_Gerente.widgets.updateBlockedActivities  import UpdateBlockedActivities
from SAP_Gerente.widgets.downloadQgisProject  import DownloadQgisProject
from SAP_Gerente.widgets.editProductionLine  import EditProductionLine
from SAP_Gerente.widgets.loadLayersQgisProject  import LoadLayersQgisProject
from SAP_Gerente.widgets.deleteFeatures  import DeleteFeatures
from SAP_Gerente.widgets.synchronizeUserInformation  import SynchronizeUserInformation
from SAP_Gerente.widgets.importUsersAuthServiceDlg  import ImportUsersAuthServiceDlg
from SAP_Gerente.widgets.mUsersPrivileges  import MUsersPrivileges
from SAP_Gerente.widgets.deleteActivities  import DeleteActivities
from SAP_Gerente.widgets.createActivities  import CreateActivities
from SAP_Gerente.widgets.resetPrivileges  import ResetPrivileges
from SAP_Gerente.widgets.revokePrivileges  import RevokePrivileges
from SAP_Gerente.widgets.mEditLayers  import MEditLayers
from SAP_Gerente.widgets.mImportLayers  import MImportLayers
from SAP_Gerente.widgets.alterBlock  import AlterBlock
from SAP_Gerente.widgets.copySetupToLocalMode  import CopySetupToLocalMode
from SAP_Gerente.widgets.createScreens  import CreateScreens
from SAP_Gerente.widgets.mFmeServers  import MFmeServers
from SAP_Gerente.widgets.mFmeProfiles  import MFmeProfiles
from SAP_Gerente.widgets.clearUserActivities  import ClearUserActivities
from SAP_Gerente.widgets.deleteAssociatedInputs  import DeleteAssociatedInputs
from SAP_Gerente.widgets.associateInputs  import AssociateInputs
from SAP_Gerente.widgets.deleteWorkUnits  import DeleteWorkUnits
from SAP_Gerente.widgets.createProduct  import CreateProduct
from SAP_Gerente.widgets.loadWorkUnit  import LoadWorkUnit
from SAP_Gerente.widgets.copyWorkUnit  import CopyWorkUnit
from SAP_Gerente.widgets.mModelProfiles  import MModelProfiles
from SAP_Gerente.widgets.mRuleProfiles  import MRuleProfiles
from SAP_Gerente.widgets.mStyleProfiles  import MStyleProfiles
from SAP_Gerente.widgets.associateUserToBlocks import AssociateUserToBlocks
from SAP_Gerente.widgets.associateUserToProfiles import AssociateUserToProfiles
from SAP_Gerente.widgets.mStyleGroups import MStyleGroups
from SAP_Gerente.widgets.mMenu  import MMenu
from SAP_Gerente.widgets.mMenuProfile  import MMenuProfile
from SAP_Gerente.widgets.mInputGroup  import MInputGroup
from SAP_Gerente.widgets.createInputs  import CreateInputs
from SAP_Gerente.widgets.createAllActivities  import CreateAllActivities
from SAP_Gerente.widgets.createDefaultSteps  import CreateDefaultSteps
from SAP_Gerente.widgets.profileProductionSetting import ProfileProductionSetting
from SAP_Gerente.widgets.deleteWorkUnitActivities import DeleteWorkUnitActivities
from SAP_Gerente.widgets.updateLayersQgisProject import UpdateLayersQgisProject
from SAP_Gerente.widgets.mProjects  import MProjects
from SAP_Gerente.widgets.mLots  import MLots
from SAP_Gerente.widgets.mBlocks  import MBlocks
from SAP_Gerente.widgets.mProductionData  import MProductionData
from SAP_Gerente.widgets.associateBlockInputs  import AssociateBlockInputs
from SAP_Gerente.widgets.revokeUserPrivileges  import RevokeUserPrivileges
from SAP_Gerente.widgets.setQgisVersion  import SetQgisVersion
from SAP_Gerente.widgets.mProfileFinalization  import MProfileFinalization
from SAP_Gerente.widgets.mAlias  import MAlias
from SAP_Gerente.widgets.mAliasProfile  import MAliasProfile
from SAP_Gerente.widgets.mPlugin  import MPlugin
from SAP_Gerente.widgets.mShortcut  import MShortcut
from SAP_Gerente.widgets.mLineage  import MLineage
from SAP_Gerente.widgets.mProblemActivity  import MProblemActivity
from SAP_Gerente.widgets.mThemes  import MThemes
from SAP_Gerente.widgets.mThemesProfile import MThemesProfile
from SAP_Gerente.widgets.mLastCompletedActivities import MLastCompletedActivities
from SAP_Gerente.widgets.mRunningActivities import MRunningActivities
from SAP_Gerente.widgets.reshapeUT import ReshapeUT
from SAP_Gerente.widgets.cutUT import CutUT
from SAP_Gerente.widgets.mergeUT import MergeUT
from SAP_Gerente.widgets.setupSAPLocal import SetupSAPLocal
from SAP_Gerente.widgets.endSAPLocal import EndSAPLocal
from SAP_Gerente.widgets.mChangeReport import MChangeReport
from SAP_Gerente.widgets.resetPropertiesUT import ResetPropertiesUT
from SAP_Gerente.widgets.setRepositoryPluginURL import SetRepositoryPluginURL
from SAP_Gerente.widgets.mProfileDifficulty import MProfileDifficulty
from SAP_Gerente.widgets.copySetupLot import CopySetupLot
from SAP_Gerente.widgets.mWorkflow import MWorkflow
from SAP_Gerente.widgets.mWorkflowProfile import MWorkflowProfile
from SAP_Gerente.widgets.mProfileMonitoring import MProfileMonitoring
from SAP_Gerente.widgets.mFilaPrioritaria import MFilaPrioritaria
from SAP_Gerente.widgets.mPIT import MPIT
from SAP_Gerente.widgets.deleteProductsWithoutUT  import DeleteProductsWithoutUT
from SAP_Gerente.widgets.deleteUTWithoutActivity  import DeleteUTWithoutActivity
from SAP_Gerente.widgets.deleteLoteWithoutProduct  import DeleteLoteWithoutProduct
from SAP_Gerente.widgets.relatorioAtividades import RelatorioAtividades
from SAP_Gerente.widgets.relatorioGeral import RelatorioGeral
from SAP_Gerente.widgets.mFields import MFields
from SAP_Gerente.widgets.mPhotos import MPhotos
from SAP_Gerente.widgets.mTrack import MTrack
from SAP_Gerente.widgets.mProdutoCampo import MProdutoCampo

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
                    "name" : 'Relatório de Atividades',
                    "widget" : lambda: RelatorioAtividades(controller, sap)
                },
                {
                    "name" : 'Relatório Geral',
                    "widget" : lambda: RelatorioGeral(controller, sap)
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
                    "name" : 'Gerenciar Fila Prioritária',
                    "widget" : lambda: MFilaPrioritaria(controller, qgis, sap)
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
                    "name" : 'Gerenciar PIT',
                    "widget" : lambda: MPIT(controller, qgis, sap)
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
                    "name" : 'Problemas Reportados',
                    "widget" : lambda: MProblemActivity(controller, qgis, sap)
                },
                {
                    'name': 'Relatório de Alterações',
                    'widget': lambda: MChangeReport(controller, qgis, sap)
                },
                {
                    "name" : 'Redesenhar Unidade de Trabalho',
                    "widget" : lambda: ReshapeUT(controller, qgis, sap)
                },
                {
                    "name" : 'Cortar Unidade de Trabalho',
                    "widget" : lambda: CutUT(controller, qgis, sap)
                },
                {
                    "name" : 'Unir Unidade de Trabalho',
                    "widget" : lambda: MergeUT(controller, qgis, sap)
                },
                {
                    'name': 'Redefinir Propriedades da Unidade de Trabalho',
                    'widget': lambda: ResetPropertiesUT(controller, qgis, sap)
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
                    "name" : 'Configurar SAP Local',
                    "widget" : lambda: SetupSAPLocal(users, controller, qgis, sap)
                },
                {
                    "name" : 'Finalizar SAP Local',
                    "widget" : lambda: EndSAPLocal(controller, qgis, sap)
                },
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
                    "name" : 'Criar Lote',
                    "widget" : lambda: MLots(controller, qgis, sap)
                },
                {
                    'name': 'Copiar Configurações do Lote',
                    'widget': lambda: CopySetupLot(sap)
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
                    "name": 'Gerenciador Grupo de Insumos',
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
                    "name": 'Configurar Perfis de Menus',
                    "widget": lambda: MMenuProfile(controller, qgis, sap)
                },
                {
                    "name" : 'Gerenciador de Alias',
                    "widget" : lambda: MAlias(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar Perfis de Alias',
                    "widget" : lambda: MAliasProfile(controller, qgis, sap)
                },
                {
                    "name": 'Gerenciador de Temas',
                    "widget": lambda: MThemes(controller, qgis, sap)
                },
                {
                    "name": 'Configurar Perfis de Temas',
                    "widget": lambda: MThemesProfile(controller, qgis, sap)
                },
                {
                    "name": 'Gerenciador de Workflows',
                    "widget": lambda: MWorkflow(controller, qgis, sap)
                },
                {
                    "name": 'Configurar Perfis de Workflows',
                    "widget": lambda: MWorkflowProfile(controller, qgis, sap)
                },
                {
                    "name": 'Configurar Perfis de Finalização',
                    "widget": lambda: MProfileFinalization(
                        controller, qgis, sap,
                        parent=instance
                    )
                },
                {
                    "name": 'Configurar Perfis de Dificuldade',
                    "widget": lambda: MProfileDifficulty(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar Perfis de Linhagem',
                    "widget" : lambda: MLineage(controller, qgis, sap)
                },
                {
                    "name": 'Configurar Perfis de Monitoramento',
                    "widget": lambda: MProfileMonitoring(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar Servidores do Gerenciador FME',
                    "widget" : lambda: MFmeServers(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar Perfis de Rotinas FME',
                    "widget" : lambda: MFmeProfiles(controller, qgis, sap, fme)
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
                    "name" : 'Editar Linhas de produção',
                    "widget" : lambda: EditProductionLine(controller, qgis, sap)
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
                    "name" : 'Deletar Produtos sem UT',
                    "widget" : lambda: DeleteProductsWithoutUT(controller)
                },
                {
                    "name" : 'Deletar UT sem atividade',
                    "widget" : lambda: DeleteUTWithoutActivity(controller)
                },
                {
                    "name" : 'Deletar Lote sem produto',
                    "widget" : lambda: DeleteLoteWithoutProduct(controller)
                }
            ]:
            dockSapBuilder.addDangerZoneWidget(functionWidget['name'], functionWidget['widget'])

        for functionWidget in [
            {
                    "name" : 'Gerenciar Campos',
                    "widget" : lambda: MFields(controller, qgis, sap)
            },
            {
                    "name" : 'Gerenciar Fotos',
                    "widget" : lambda: MPhotos(controller, qgis, sap)
            },
            {
                "name": 'Gerenciar Tracker',
                "widget": lambda: MTrack(controller, qgis, sap)
            },
            {
                "name": "Gerenciar Campos e Produtos",
                "widget": lambda: MProdutoCampo(controller, qgis, sap)
            }
        ]:
            dockSapBuilder.addFieldsWidget(functionWidget['name'], functionWidget['widget'])
            
            
