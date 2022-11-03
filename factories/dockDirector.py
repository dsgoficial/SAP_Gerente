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
from Ferramentas_Gerencia.widgets.openMStyles  import OpenMStyles
from Ferramentas_Gerencia.widgets.openMModels  import OpenMModels
from Ferramentas_Gerencia.widgets.openMRules  import OpenMRules
from Ferramentas_Gerencia.widgets.generatesWorkUnit  import GeneratesWorkUnit
from Ferramentas_Gerencia.widgets.updateBlockedActivities  import UpdateBlockedActivities
from Ferramentas_Gerencia.widgets.downloadQgisProject  import DownloadQgisProject
from Ferramentas_Gerencia.widgets.loadLayersQgisProject  import LoadLayersQgisProject
from Ferramentas_Gerencia.widgets.deleteFeatures  import DeleteFeatures
from Ferramentas_Gerencia.widgets.synchronizeUserInformation  import SynchronizeUserInformation
from Ferramentas_Gerencia.widgets.openUsersAuthService  import OpenUsersAuthService
from Ferramentas_Gerencia.widgets.openMUsersPrivileges  import OpenMUsersPrivileges
from Ferramentas_Gerencia.widgets.deleteActivities  import DeleteActivities
from Ferramentas_Gerencia.widgets.createActivities  import CreateActivities
from Ferramentas_Gerencia.widgets.resetPrivileges  import ResetPrivileges
from Ferramentas_Gerencia.widgets.revokePrivileges  import RevokePrivileges
from Ferramentas_Gerencia.widgets.setupLayers  import SetupLayers
from Ferramentas_Gerencia.widgets.importLayers  import ImportLayers
from Ferramentas_Gerencia.widgets.alterBlock  import AlterBlock
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
from Ferramentas_Gerencia.widgets.openMModelProfiles  import OpenMModelProfiles
from Ferramentas_Gerencia.widgets.openMRuleProfiles  import OpenMRuleProfiles
from Ferramentas_Gerencia.widgets.openMStyleProfiles  import OpenMStyleProfiles
from Ferramentas_Gerencia.widgets.openAssociateUserToBlocks import OpenAssociateUserToBlocks
from Ferramentas_Gerencia.widgets.openAssociateUserToProfiles import OpenAssociateUserToProfiles
from Ferramentas_Gerencia.widgets.openAssociateUserToProfiles import OpenAssociateUserToProfiles
from Ferramentas_Gerencia.widgets.openMStyleGroups import OpenMStyleGroups
from Ferramentas_Gerencia.widgets.openMMenu  import OpenMMenu
from Ferramentas_Gerencia.widgets.openMMenuProfile  import OpenMMenuProfile

class DockDirector:

    #interface
    def constructSapMDock(self, dockSapBuilder, controller):
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
                    "widget" : OpenMStyles(controller)
                },
                {
                    "name" : 'Gerenciador grupo estilos',
                    "widget" : OpenMStyleGroups(controller)
                },
                {
                    "name" : 'Configurar perfis de estilos',
                    "widget" : OpenMStyleProfiles(controller)
                },
                {
                    "name" : 'Gerenciador de modelos',
                    "widget" : OpenMModels(controller)
                },
                {
                    "name" : 'Configurar perfis de modelos',
                    "widget" : OpenMModelProfiles(controller)
                },
                {
                    "name" : 'Gerenciador de regras',
                    "widget" : OpenMRules(controller)
                },
                {
                    "name" : 'Configurar perfis de regras',
                    "widget" : OpenMRuleProfiles(controller)
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
                    "widget" : OpenUsersAuthService(controller)
                },
                {
                    "name" : 'Sincronizar informações de usuários',
                    "widget" : SynchronizeUserInformation(controller)
                },
                {
                    "name" : 'Modificar permissões de usuários',
                    "widget" : OpenMUsersPrivileges(controller)
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
                    "name" : 'Alterar Bloco',
                    "widget" : AlterBlock(controller)
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
                    "name": 'Associar usuário à blocos',
                    "widget": OpenAssociateUserToBlocks(
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
                },
                {
                    "name": 'Gerenciador de menu',
                    "widget": OpenMMenu(controller)
                },
                {
                    "name": 'Gerenciador perfis de menu',
                    "widget": OpenMMenuProfile(controller)
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
            
            
