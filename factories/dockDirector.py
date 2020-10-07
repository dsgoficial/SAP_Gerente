from Ferramentas_Gerencia.dockWidgets.addNewRevision  import AddNewRevision
from Ferramentas_Gerencia.dockWidgets.addNewRevisionCorrection  import AddNewRevisionCorrection
from Ferramentas_Gerencia.dockWidgets.advanceActivityToNextStep  import AdvanceActivityToNextStep
from Ferramentas_Gerencia.dockWidgets.createPriorityGroupActivity  import CreatePriorityGroupActivity
from Ferramentas_Gerencia.dockWidgets.openNextActivityByUser  import OpenNextActivityByUser
from Ferramentas_Gerencia.dockWidgets.fillComments  import FillComments
from Ferramentas_Gerencia.dockWidgets.openActivity  import OpenActivity
from Ferramentas_Gerencia.dockWidgets.lockWorkspace  import LockWorkspace
from Ferramentas_Gerencia.dockWidgets.pauseActivity  import PauseActivity
from Ferramentas_Gerencia.dockWidgets.unlockWorkspace  import UnlockWorkspace
from Ferramentas_Gerencia.dockWidgets.restartActivity  import RestartActivity
from Ferramentas_Gerencia.dockWidgets.setPriorityActivity  import SetPriorityActivity
from Ferramentas_Gerencia.dockWidgets.returnActivityToPreviousStep  import ReturnActivityToPreviousStep
from Ferramentas_Gerencia.dockWidgets.managementStyles  import ManagementStyles
from Ferramentas_Gerencia.dockWidgets.managementModels  import ManagementModels
from Ferramentas_Gerencia.dockWidgets.managementRules  import ManagementRules
from Ferramentas_Gerencia.dockWidgets.generatesWorkUnit  import GeneratesWorkUnit
from Ferramentas_Gerencia.dockWidgets.updateBlockedActivities  import UpdateBlockedActivities
from Ferramentas_Gerencia.dockWidgets.downloadQgisProject  import DownloadQgisProject
from Ferramentas_Gerencia.dockWidgets.loadLayersQgisProject  import LoadLayersQgisProject
from Ferramentas_Gerencia.dockWidgets.deleteFeatures  import DeleteFeatures
from Ferramentas_Gerencia.dockWidgets.synchronizeUserInformation  import SynchronizeUserInformation
from Ferramentas_Gerencia.dockWidgets.importUsersAuthService  import ImportUsersAuthService
from Ferramentas_Gerencia.dockWidgets.importUsersAuthService  import ImportUsersAuthService
from Ferramentas_Gerencia.dockWidgets.managementUsersPrivileges  import ManagementUsersPrivileges
from Ferramentas_Gerencia.dockWidgets.deleteActivities  import DeleteActivities
from Ferramentas_Gerencia.dockWidgets.createActivities  import CreateActivities
from Ferramentas_Gerencia.dockWidgets.resetPrivileges  import ResetPrivileges
from Ferramentas_Gerencia.dockWidgets.revokePrivileges  import RevokePrivileges
from Ferramentas_Gerencia.dockWidgets.setupLayers  import SetupLayers
from Ferramentas_Gerencia.dockWidgets.importLayers  import ImportLayers
from Ferramentas_Gerencia.dockWidgets.alterLot  import AlterLot
from Ferramentas_Gerencia.dockWidgets.copySetupToLocalMode  import CopySetupToLocalMode
from Ferramentas_Gerencia.dockWidgets.createScreens  import CreateScreens
from Ferramentas_Gerencia.dockWidgets.setupFmeServers  import SetupFmeServers
from Ferramentas_Gerencia.dockWidgets.setupFmeProfiles  import SetupFmeProfiles
from Ferramentas_Gerencia.dockWidgets.clearUserActivities  import ClearUserActivities
from Ferramentas_Gerencia.dockWidgets.deleteAssociatedInputs  import DeleteAssociatedInputs
from Ferramentas_Gerencia.dockWidgets.associateInputs  import AssociateInputs
from Ferramentas_Gerencia.dockWidgets.deleteWorkUnits  import DeleteWorkUnits
from Ferramentas_Gerencia.dockWidgets.deleteRevisionCorrection  import DeleteRevisionCorrection
from Ferramentas_Gerencia.dockWidgets.createProduct  import CreateProduct
from Ferramentas_Gerencia.dockWidgets.loadWorkUnit  import LoadWorkUnit
from Ferramentas_Gerencia.dockWidgets.copyWorkUnit  import CopyWorkUnit

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
                    "widget" : ManagementStyles(managementToolCtrl)
                },
                {
                    "name" : 'Gerenciador de modelos',
                    "widget" : ManagementModels(managementToolCtrl)
                },
                {
                    "name" : 'Gerenciador de regras',
                    "widget" : ManagementRules(managementToolCtrl)
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
                    "name" : 'Adicionar nova revisão',
                    "widget" : AddNewRevision(managementToolCtrl)
                },
                {
                    "name" : 'Adicionar nova revisão/correção',
                    "widget" : AddNewRevisionCorrection(managementToolCtrl)
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
                    "widget" : ManagementUsersPrivileges(managementToolCtrl)
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
                },
                {
                    "name" : 'Deletar revisão e correção',
                    "widget" : DeleteRevisionCorrection(managementToolCtrl)
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
            
            