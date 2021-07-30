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


class DockDirector:

    #interface
    def constructSapManagementDock(self, dockSapBuilder, managementToolCtrl):
        users = managementToolCtrl.getSapUsers()
        databases = managementToolCtrl.getSapDatabases()
        inputGroups = managementToolCtrl.getSapInputGroups()
        #management project tab
        for functionWidget in [
                {
                    "name" : 'Abrir atividade',
                    "widget" : OpenActivity(managementToolCtrl)
                },
                {
                    "name" : 'Abrir atividade do operador',
                    "widget" : OpenNextActivityByUser(users, managementToolCtrl)
                },
                {
                    "name" : 'Bloquear unidades de trabalho',
                    "widget" : LockWorkspace(managementToolCtrl)
                },
                {
                    "name" : 'Desbloquear unidades de trabalho',
                    "widget" : UnlockWorkspace(managementToolCtrl)
                },
                {
                    "name" : 'Pausar atividades em execução',
                    "widget" : PauseActivity(managementToolCtrl)
                },
                {
                    "name" : 'Reiniciar atividades em execução ou pausadas',
                    "widget" : RestartActivity(managementToolCtrl)
                },
                {
                    "name" : 'Definir atividades prioritárias',
                    "widget" : SetPriorityActivity(users, managementToolCtrl)
                },
                {
                    "name" : 'Definir atividades prioritárias de grupo',
                    "widget" : CreatePriorityGroupActivity(managementToolCtrl)
                },
                {
                    "name" : 'Avançar atividades para próxima etapa',
                    "widget" : AdvanceActivityToNextStep(managementToolCtrl)
                },
                {
                    "name" : 'Retornar atividades para etapa anterior',
                    "widget" : ReturnActivityToPreviousStep(managementToolCtrl)
                },
                {
                    "name" : 'Preencher observações',
                    "widget" : FillComments(managementToolCtrl)
                },
                {
                    "name" : 'Carregar camadas de acompanhamento',
                    "widget" : LoadLayersQgisProject(managementToolCtrl)
                },
                {
                    "name" : 'Criar telas de acompanhamento',
                    "widget" : CreateScreens(managementToolCtrl)
                },
                {
                    "name" : 'Redefinir permissões',
                    "widget" : ResetPrivileges(managementToolCtrl)
                },
                {
                    "name" : 'Revogar permissões',
                    "widget" : RevokePrivileges(databases, managementToolCtrl)
                },
                {
                    "name" : 'Copiar configurações para modo local',
                    "widget" : CopySetupToLocalMode(databases, managementToolCtrl)
                },
                {
                    "name" : 'Atualizar atividades bloqueadas',
                    "widget" : UpdateBlockedActivities(managementToolCtrl)
                }
            ]:
            dockSapBuilder.addProjectManagementWidget(functionWidget['name'], functionWidget['widget'])
        #creation project tab
        for functionWidget in [
                {
                    "name" : 'Gerar projeto de acompanhamento',
                    "widget" : DownloadQgisProject(managementToolCtrl)
                },
                {
                    "name" : 'Gerenciador de estilos',
                    "widget" : OpenManagementStyles(managementToolCtrl)
                },
                {
                    "name" : 'Configurar perfis de estilos',
                    "widget" : OpenManagementStyleProfiles(managementToolCtrl)
                },
                {
                    "name" : 'Gerenciador de modelos',
                    "widget" : OpenManagementModels(managementToolCtrl)
                },
                {
                    "name" : 'Configurar perfis de modelos',
                    "widget" : OpenManagementModelProfiles(managementToolCtrl)
                },
                {
                    "name" : 'Gerenciador de regras',
                    "widget" : OpenManagementRules(managementToolCtrl)
                },
                {
                    "name" : 'Configurar perfis de regras',
                    "widget" : OpenManagementRuleProfiles(managementToolCtrl)
                },
                {
                    "name" : 'Configurar servidores do gerenciador FME',
                    "widget" : SetupFmeServers(managementToolCtrl)
                },
                {
                    "name" : 'Configurar perfil de rotinas FME',
                    "widget" : SetupFmeProfiles(managementToolCtrl)
                },
                {
                    "name" : 'Gera unidades de trabalho',
                    "widget" : GeneratesWorkUnit(managementToolCtrl.getQgisComboBoxPolygonLayer(), managementToolCtrl)
                },
                {
                    "name" : 'Carregar unidades de trabalho',
                    "widget" : LoadWorkUnit(managementToolCtrl.getQgisComboBoxPolygonLayer(), managementToolCtrl)
                },
                {
                    "name" : 'Copiar unidades de trabalho',
                    "widget" : CopyWorkUnit(managementToolCtrl)
                },
                {
                    "name" : 'Criar atividades',
                    "widget" : CreateActivities(managementToolCtrl)
                },
                {
                    "name" : 'Deletar atividades',
                    "widget" : DeleteActivities(managementToolCtrl)
                },
                {
                    "name" : 'Importar usuários',
                    "widget" : ImportUsersAuthService(managementToolCtrl)
                },
                {
                    "name" : 'Sincronizar informações de usuários',
                    "widget" : SynchronizeUserInformation(managementToolCtrl)
                },
                {
                    "name" : 'Modificar permissões usuários',
                    "widget" : OpenManagementUsersPrivileges(managementToolCtrl)
                },
                {
                    "name" : 'Importar camadas',
                    "widget" : ImportLayers(managementToolCtrl)
                },
                {
                    "name" : 'Configurar camadas',
                    "widget" : SetupLayers(managementToolCtrl)
                },
                {
                    "name" : 'Alterar lote',
                    "widget" : AlterLot(managementToolCtrl)
                },
                {
                    "name" : 'Criar produtos',
                    "widget" : CreateProduct(managementToolCtrl.getQgisComboBoxPolygonLayer(), managementToolCtrl)
                },
                {
                    "name" : 'Associar insumos',
                    "widget" : AssociateInputs(inputGroups, managementToolCtrl)
                },
                {
                    "name" : 'Deletar insumos associados',
                    "widget" : DeleteAssociatedInputs(inputGroups, managementToolCtrl)
                },
                {
                    "name" : 'Deletar unidades de trabalho',
                    "widget" : DeleteWorkUnits(managementToolCtrl)
                }
            ]:
            dockSapBuilder.addProjectCreationWidget(functionWidget['name'], functionWidget['widget'])
        #danger zone tab
        
        for functionWidget in [
                {
                    "name" : 'Remover feições em área',
                    "widget" : DeleteFeatures(managementToolCtrl)
                },
                {
                    "name" : 'Limpar atividades de usuário',
                    "widget" : ClearUserActivities(users, managementToolCtrl)
                }
            ]:
            dockSapBuilder.addDangerZoneWidget(functionWidget['name'], functionWidget['widget'])
            
            