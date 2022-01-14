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
from Ferramentas_Gerencia.widgets.openManagementStyles  import OpenManagementStyles
from Ferramentas_Gerencia.widgets.openManagementModels  import OpenManagementModels
from Ferramentas_Gerencia.widgets.openManagementRules  import OpenManagementRules
from Ferramentas_Gerencia.widgets.generatesWorkUnit  import GeneratesWorkUnit
from Ferramentas_Gerencia.widgets.updateBlockedActivities  import UpdateBlockedActivities
from Ferramentas_Gerencia.widgets.downloadQgisProject  import DownloadQgisProject
from Ferramentas_Gerencia.widgets.loadLayersQgisProject  import LoadLayersQgisProject
from Ferramentas_Gerencia.widgets.deleteFeatures  import DeleteFeatures
from Ferramentas_Gerencia.widgets.synchronizeUserInformation  import SynchronizeUserInformation
from Ferramentas_Gerencia.widgets.importUsersAuthService  import ImportUsersAuthService
from Ferramentas_Gerencia.widgets.importUsersAuthService  import ImportUsersAuthService
from Ferramentas_Gerencia.widgets.openManagementUsersPrivileges  import OpenManagementUsersPrivileges
from Ferramentas_Gerencia.widgets.deleteActivities  import DeleteActivities
from Ferramentas_Gerencia.widgets.createActivities  import CreateActivities
from Ferramentas_Gerencia.widgets.resetPrivileges  import ResetPrivileges
from Ferramentas_Gerencia.widgets.revokePrivileges  import RevokePrivileges
from Ferramentas_Gerencia.widgets.setupLayers  import SetupLayers
from Ferramentas_Gerencia.widgets.importLayers  import ImportLayers
from Ferramentas_Gerencia.widgets.alterLot  import AlterLot
from Ferramentas_Gerencia.widgets.copySetupToLocalMode  import CopySetupToLocalMode
from Ferramentas_Gerencia.widgets.createScreens  import CreateScreens
from Ferramentas_Gerencia.widgets.setupFmeServers  import SetupFmeServers
from Ferramentas_Gerencia.widgets.setupFmeProfiles  import SetupFmeProfiles
from Ferramentas_Gerencia.widgets.clearUserActivities  import ClearUserActivities
from Ferramentas_Gerencia.widgets.deleteAssociatedInputs  import DeleteAssociatedInputs
from Ferramentas_Gerencia.widgets.associateInputs  import AssociateInputs
from Ferramentas_Gerencia.widgets.deleteWorkUnits  import DeleteWorkUnits
from Ferramentas_Gerencia.widgets.createProduct  import CreateProduct
from Ferramentas_Gerencia.widgets.loadWorkUnit  import LoadWorkUnit
from Ferramentas_Gerencia.widgets.copyWorkUnit  import CopyWorkUnit
from Ferramentas_Gerencia.widgets.openManagementModelProfiles  import OpenManagementModelProfiles
from Ferramentas_Gerencia.widgets.openManagementRuleProfiles  import OpenManagementRuleProfiles
from Ferramentas_Gerencia.widgets.openManagementStyleProfiles  import OpenManagementStyleProfiles
from Ferramentas_Gerencia.widgets.openAssociateUserToProjects import OpenAssociateUserToProjects
from Ferramentas_Gerencia.widgets.openAssociateUserToProfiles import OpenAssociateUserToProfiles

class DockDirector:

    #interface
    def constructSapManagementDock(self, dockSapBuilder, controller):
        users = controller.getSapUsers()
        databases = controller.getSapDatabases()
        inputGroups = controller.getSapInputGroups()
        instance = dockSapBuilder.getInstance()
        dockSapBuilder.setController(controller)
        #management project tab
        for functionWidget in [
                {
                    "name" : 'Abrir atividade',
                    "widget" : OpenActivity(controller)
                },
                {
                    "name" : 'Abrir atividade do operador',
                    "widget" : OpenNextActivityByUser(users, controller)
                },
                {
                    "name" : 'Bloquear unidades de trabalho',
                    "widget" : LockWorkspace(controller)
                },
                {
                    "name" : 'Desbloquear unidades de trabalho',
                    "widget" : UnlockWorkspace(controller)
                },
                {
                    "name" : 'Pausar atividades em execução',
                    "widget" : PauseActivity(controller)
                },
                {
                    "name" : 'Reiniciar atividades em execução ou pausadas',
                    "widget" : RestartActivity(controller)
                },
                {
                    "name" : 'Definir atividades prioritárias',
                    "widget" : SetPriorityActivity(users, controller)
                },
                {
                    "name" : 'Definir atividades prioritárias de grupo',
                    "widget" : CreatePriorityGroupActivity(controller)
                },
                {
                    "name" : 'Avançar atividades para próxima etapa',
                    "widget" : AdvanceActivityToNextStep(controller)
                },
                {
                    "name" : 'Retornar atividades para etapa anterior',
                    "widget" : ReturnActivityToPreviousStep(controller)
                },
                {
                    "name" : 'Preencher observações',
                    "widget" : FillComments(controller)
                },
                {
                    "name" : 'Carregar camadas de acompanhamento',
                    "widget" : LoadLayersQgisProject(controller)
                },
                {
                    "name" : 'Criar telas de acompanhamento',
                    "widget" : CreateScreens(controller)
                },
                {
                    "name" : 'Redefinir permissões',
                    "widget" : ResetPrivileges(controller)
                },
                {
                    "name" : 'Revogar permissões',
                    "widget" : RevokePrivileges(databases, controller)
                },
                {
                    "name" : 'Copiar configurações para modo local',
                    "widget" : CopySetupToLocalMode(databases, controller)
                },
                {
                    "name" : 'Atualizar atividades bloqueadas',
                    "widget" : UpdateBlockedActivities(controller)
                }
            ]:
            dockSapBuilder.addProjectManagementWidget(functionWidget['name'], functionWidget['widget'])
        #creation project tab
        for functionWidget in [
                {
                    "name" : 'Gerar projeto de acompanhamento',
                    "widget" : DownloadQgisProject(controller)
                },
                {
                    "name" : 'Gerenciador de estilos',
                    "widget" : OpenManagementStyles(controller)
                },
                {
                    "name" : 'Configurar perfis de estilos',
                    "widget" : OpenManagementStyleProfiles(controller)
                },
                {
                    "name" : 'Gerenciador de modelos',
                    "widget" : OpenManagementModels(controller)
                },
                {
                    "name" : 'Configurar perfis de modelos',
                    "widget" : OpenManagementModelProfiles(controller)
                },
                {
                    "name" : 'Gerenciador de regras',
                    "widget" : OpenManagementRules(controller)
                },
                {
                    "name" : 'Configurar perfis de regras',
                    "widget" : OpenManagementRuleProfiles(controller)
                },
                {
                    "name" : 'Configurar servidores do gerenciador FME',
                    "widget" : SetupFmeServers(controller)
                },
                {
                    "name" : 'Configurar perfil de rotinas FME',
                    "widget" : SetupFmeProfiles(controller)
                },
                {
                    "name" : 'Gera unidades de trabalho',
                    "widget" : GeneratesWorkUnit(controller.getQgisComboBoxPolygonLayer(), controller)
                },
                {
                    "name" : 'Carregar unidades de trabalho',
                    "widget" : LoadWorkUnit(controller.getQgisComboBoxPolygonLayer(), controller)
                },
                {
                    "name" : 'Copiar unidades de trabalho',
                    "widget" : CopyWorkUnit(controller)
                },
                {
                    "name" : 'Criar atividades',
                    "widget" : CreateActivities(controller)
                },
                {
                    "name" : 'Deletar atividades',
                    "widget" : DeleteActivities(controller)
                },
                {
                    "name" : 'Importar usuários',
                    "widget" : ImportUsersAuthService(controller)
                },
                {
                    "name" : 'Sincronizar informações de usuários',
                    "widget" : SynchronizeUserInformation(controller)
                },
                {
                    "name" : 'Modificar permissões usuários',
                    "widget" : OpenManagementUsersPrivileges(controller)
                },
                {
                    "name" : 'Importar camadas',
                    "widget" : ImportLayers(controller)
                },
                {
                    "name" : 'Configurar camadas',
                    "widget" : SetupLayers(controller)
                },
                {
                    "name" : 'Alterar lote',
                    "widget" : AlterLot(controller)
                },
                {
                    "name" : 'Criar produtos',
                    "widget" : CreateProduct(controller.getQgisComboBoxPolygonLayer(), controller)
                },
                {
                    "name" : 'Associar insumos',
                    "widget" : AssociateInputs(inputGroups, controller)
                },
                {
                    "name" : 'Deletar insumos associados',
                    "widget" : DeleteAssociatedInputs(inputGroups, controller)
                },
                {
                    "name" : 'Deletar unidades de trabalho',
                    "widget" : DeleteWorkUnits(controller)
                },
                {
                    "name": 'Associar usuário à projetos',
                    "widget": OpenAssociateUserToProjects(
                        controller,
                        parent=instance
                    )
                },
                {
                    "name": 'Associar usuário à perfis de produção',
                    "widget": OpenAssociateUserToProfiles(
                        controller,
                        parent=instance
                    )
                }
            ]:
            dockSapBuilder.addProjectCreationWidget(functionWidget['name'], functionWidget['widget'])
        #danger zone tab
        
        for functionWidget in [
                {
                    "name" : 'Remover feições em área',
                    "widget" : DeleteFeatures(controller)
                },
                {
                    "name" : 'Limpar atividades de usuário',
                    "widget" : ClearUserActivities(users, controller)
                }
            ]:
            dockSapBuilder.addDangerZoneWidget(functionWidget['name'], functionWidget['widget'])
            
            
