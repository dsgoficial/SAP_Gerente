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

class DockDirector:

    #interface
    def constructSapMDock(self, dockSapBuilder, controller, qgis, sap, fme):
        users = controller.getSapUsers()
        databases = controller.getSapDatabases()
        instance = None #dockSapBuilder.getInstance()
        dockSapBuilder.setController(controller)
        #management project tab
        for functionWidget in [
                {
                    "name" : 'Abrir atividade',
                    "widget" : lambda: OpenActivity(controller)
                },
                {
                    "name" : 'Abrir atividade do operador',
                    "widget" : lambda: OpenNextActivityByUser(users, controller)
                },
                {
                    "name" : 'Bloquear unidades de trabalho',
                    "widget" : lambda: LockWorkspace(controller)
                },
                {
                    "name" : 'Desbloquear unidades de trabalho',
                    "widget" : lambda: UnlockWorkspace(controller)
                },
                {
                    "name" : 'Pausar atividades em execução',
                    "widget" : lambda: PauseActivity(controller)
                },
                {
                    "name" : 'Reiniciar atividades em execução ou pausadas',
                    "widget" : lambda: RestartActivity(controller)
                },
                {
                    "name" : 'Definir atividades prioritárias',
                    "widget" : lambda: SetPriorityActivity(controller, qgis, sap)
                },
                {
                    "name" : 'Definir atividades prioritárias de grupo',
                    "widget" : lambda: CreatePriorityGroupActivity(controller, qgis, sap)
                },
                {
                    "name" : 'Avançar atividades para próxima etapa',
                    "widget" : lambda: AdvanceActivityToNextStep(controller)
                },
                {
                    "name" : 'Retornar atividades para etapa anterior',
                    "widget" : lambda: ReturnActivityToPreviousStep(controller)
                },
                {
                    "name" : 'Preencher observações',
                    "widget" : lambda: FillComments(controller)
                },
                {
                    "name" : 'Carregar camadas de acompanhamento',
                    "widget" : lambda: LoadLayersQgisProject(controller)
                },
                {
                    "name" : 'Atualizar camadas de acompanhamento',
                    "widget" : lambda: UpdateLayersQgisProject(controller, sap)
                },
                {
                    "name" : 'Criar telas de acompanhamento',
                    "widget" : lambda: CreateScreens(controller)
                },
                {
                    "name" : 'Redefinir permissões',
                    "widget" : lambda: ResetPrivileges(controller)
                },
                {
                    "name" : 'Revogar permissões',
                    "widget" : lambda: RevokePrivileges(databases, controller)
                },
                {
                    "name" : 'Copiar configurações para modo local',
                    "widget" : lambda: CopySetupToLocalMode(databases, controller)
                }
            ]:
            dockSapBuilder.addProjectManagementWidget(functionWidget['name'], functionWidget['widget'])
        #creation project tab
        for functionWidget in [
                {
                    "name" : 'Gerenciador de estilos',
                    "widget" : lambda: MStyles(controller, qgis, sap)
                },
                {
                    "name" : 'Gerenciador grupo estilos',
                    "widget" : lambda: MStyleGroups(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar perfis de estilos',
                    "widget" : lambda: MStyleProfiles(controller, qgis, sap)
                },
                {
                    "name" : 'Gerenciador de modelos',
                    "widget" : lambda: MModels(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar perfis de modelos',
                    "widget" : lambda: MModelProfiles(controller, qgis, sap)
                },
                {
                    "name" : 'Gerenciador de regras',
                    "widget" : lambda: MRules(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar perfis de regras',
                    "widget" : lambda: MRuleProfiles(controller, qgis, sap)
                },
                {
                    "name": 'Gerenciador de menu',
                    "widget": lambda: MMenu(controller, qgis, sap)
                },
                {
                    "name": 'Configurar perfis de menu',
                    "widget": lambda: MMenuProfile(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar servidores do gerenciador FME',
                    "widget" : lambda: MFmeServers(controller, qgis, sap)
                },
                {
                    "name" : 'Configurar perfil de rotinas FME',
                    "widget" : lambda: MFmeProfiles(controller, qgis, sap, fme)
                },
                {
                    "name" : 'Gera unidades de trabalho',
                    "widget" : lambda: GeneratesWorkUnit(controller.getQgisComboBoxPolygonLayer(), controller)
                },
                {
                    "name" : 'Carregar unidades de trabalho',
                    "widget" : lambda: LoadWorkUnit(controller.getQgisComboBoxPolygonLayer(), controller)
                },
                {
                    "name" : 'Copiar unidades de trabalho',
                    "widget" : lambda: CopyWorkUnit(controller)
                },
                {
                    "name" : 'Criar atividades',
                    "widget" : lambda: CreateActivities(controller)
                },
                {
                    "name" : 'Deletar atividades não iniciadas',
                    "widget" : lambda: DeleteActivities(controller)
                },
                {
                    "name" : 'Importar usuários',
                    "widget" : lambda: ImportUsersAuthServiceDlg(controller, qgis, sap)
                },
                {
                    "name" : 'Sincronizar informações de usuários',
                    "widget" : lambda: SynchronizeUserInformation(controller)
                },
                {
                    "name" : 'Modificar permissões de usuários',
                    "widget" : lambda: MUsersPrivileges(controller, qgis, sap)
                },
                {
                    "name" : 'Importar camadas',
                    "widget" : lambda: MImportLayers(controller)
                },
                {
                    "name" : 'Configurar camadas',
                    "widget" : lambda: MEditLayers(controller, qgis, sap)
                },
                {
                    "name" : 'Alterar Bloco',
                    "widget" : lambda: AlterBlock(controller)
                },
                {
                    "name" : 'Criar produtos',
                    "widget" : lambda: CreateProduct(controller.getQgisComboBoxPolygonLayer(), controller)
                },
                {
                    "name" : 'Associar insumos',
                    "widget" : lambda: AssociateInputs(controller.getSapInputGroups(), controller)
                },
                {
                    "name" : 'Deletar insumos associados',
                    "widget" : lambda: DeleteAssociatedInputs(controller.getSapInputGroups(), controller)
                },
                {
                    "name" : 'Deletar unidades de trabalho',
                    "widget" : lambda: DeleteWorkUnits(controller)
                },
                {
                    "name": 'Associar usuário à blocos',
                    "widget": lambda: AssociateUserToBlocks(
                        controller, qgis, sap,
                        parent=instance
                    )
                },
                {
                    "name": 'Associar usuário à perfis de produção',
                    "widget": lambda: AssociateUserToProfiles(
                        controller, qgis, sap,
                        parent=instance
                    )
                },
                {
                    "name": 'Gerenciar perfis de produção',
                    "widget": lambda: ProfileProductionSetting(
                        controller, qgis, sap,
                        parent=instance
                    )
                },
                {
                    "name": 'Configurar grupo insumos',
                    "widget": lambda: MInputGroup(controller, qgis, sap)
                },
                {
                    "name": 'Criar insumos',
                    "widget": lambda: CreateInputs(controller, qgis, sap)
                },
                {
                    "name" : 'Criar todas as atividades',
                    "widget" : lambda: CreateAllActivities(controller)
                },
                {
                    "name" : 'Criar Etapas padrão',
                    "widget" : lambda: CreateDefaultSteps(controller)
                },
                {
                    "name" : 'Deletar atividades de unidade de trabalho',
                    "widget" : lambda: DeleteWorkUnitActivities(controller, sap)
                },
            ]:
            dockSapBuilder.addProjectCreationWidget(functionWidget['name'], functionWidget['widget'])
        #danger zone tab
        
        for functionWidget in [
                {
                    "name" : 'Gerar projeto de acompanhamento',
                    "widget" : lambda: DownloadQgisProject(controller)
                },
                {
                    "name" : 'Remover feições em área',
                    "widget" : lambda: DeleteFeatures(controller)
                },
                {
                    "name" : 'Limpar atividades de usuário',
                    "widget" : lambda: ClearUserActivities(users, controller)
                }
            ]:
            dockSapBuilder.addDangerZoneWidget(functionWidget['name'], functionWidget['widget'])
            
            
