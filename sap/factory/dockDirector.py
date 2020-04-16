from Ferramentas_Gerencia.sap.dockWidgets.addNewRevision  import AddNewRevision
from Ferramentas_Gerencia.sap.dockWidgets.addNewRevisionCorrection  import AddNewRevisionCorrection
from Ferramentas_Gerencia.sap.dockWidgets.advanceActivityToNextStep  import AdvanceActivityToNextStep
from Ferramentas_Gerencia.sap.dockWidgets.createPriorityGroupActivity  import CreatePriorityGroupActivity
from Ferramentas_Gerencia.sap.dockWidgets.openNextActivityByUser  import OpenNextActivityByUser
from Ferramentas_Gerencia.sap.dockWidgets.fillComments  import FillComments
from Ferramentas_Gerencia.sap.dockWidgets.openActivity  import OpenActivity
from Ferramentas_Gerencia.sap.dockWidgets.lockWorkspace  import LockWorkspace
from Ferramentas_Gerencia.sap.dockWidgets.pauseActivity  import PauseActivity
from Ferramentas_Gerencia.sap.dockWidgets.unlockWorkspace  import UnlockWorkspace
from Ferramentas_Gerencia.sap.dockWidgets.restartActivity  import RestartActivity
from Ferramentas_Gerencia.sap.dockWidgets.setPriorityActivity  import SetPriorityActivity
from Ferramentas_Gerencia.sap.dockWidgets.returnActivityToPreviousStep  import ReturnActivityToPreviousStep
from Ferramentas_Gerencia.sap.dockWidgets.managementStyles  import ManagementStyles
from Ferramentas_Gerencia.sap.dockWidgets.managementModels  import ManagementModels
from Ferramentas_Gerencia.sap.dockWidgets.managementRules  import ManagementRules
from Ferramentas_Gerencia.sap.dockWidgets.generatesWorkUnit  import GeneratesWorkUnit
from Ferramentas_Gerencia.sap.dockWidgets.updateBlockedActivities  import UpdateBlockedActivities
from Ferramentas_Gerencia.sap.dockWidgets.downloadQgisProject  import DownloadQgisProject
from Ferramentas_Gerencia.sap.dockWidgets.loadLayersQgisProject  import LoadLayersQgisProject
from Ferramentas_Gerencia.sap.dockWidgets.deleteFeatures  import DeleteFeatures
from Ferramentas_Gerencia.sap.dockWidgets.synchronizeUserInformation  import SynchronizeUserInformation
from Ferramentas_Gerencia.sap.dockWidgets.importUsersAuthService  import ImportUsersAuthService
from Ferramentas_Gerencia.sap.dockWidgets.importUsersAuthService  import ImportUsersAuthService
from Ferramentas_Gerencia.sap.dockWidgets.managementUsersPrivileges  import ManagementUsersPrivileges
from Ferramentas_Gerencia.sap.dockWidgets.deleteActivities  import DeleteActivities
from Ferramentas_Gerencia.sap.dockWidgets.createActivities  import CreateActivities
from Ferramentas_Gerencia.sap.dockWidgets.resetPrivileges  import ResetPrivileges
from Ferramentas_Gerencia.sap.dockWidgets.revokePrivileges  import RevokePrivileges
from Ferramentas_Gerencia.sap.dockWidgets.setupLayers  import SetupLayers
from Ferramentas_Gerencia.sap.dockWidgets.importLayers  import ImportLayers
from Ferramentas_Gerencia.sap.dockWidgets.alterLot  import AlterLot
from Ferramentas_Gerencia.sap.dockWidgets.copySetupToLocalMode  import CopySetupToLocalMode
from Ferramentas_Gerencia.sap.dockWidgets.createScreens  import CreateScreens
from Ferramentas_Gerencia.sap.dockWidgets.setupFmeServers  import SetupFmeServers
from Ferramentas_Gerencia.sap.dockWidgets.setupFmeProfiles  import SetupFmeProfiles
from Ferramentas_Gerencia.sap.dockWidgets.clearUserActivities  import ClearUserActivities
from Ferramentas_Gerencia.sap.dockWidgets.deleteAssociatedInputs  import DeleteAssociatedInputs
from Ferramentas_Gerencia.sap.dockWidgets.associateInputs  import AssociateInputs
from Ferramentas_Gerencia.sap.dockWidgets.deleteWorkUnits  import DeleteWorkUnits
from Ferramentas_Gerencia.sap.dockWidgets.deleteRevisionCorrection  import DeleteRevisionCorrection
from Ferramentas_Gerencia.sap.dockWidgets.createProduct  import CreateProduct
from Ferramentas_Gerencia.sap.dockWidgets.loadWorkUnit  import LoadWorkUnit
from Ferramentas_Gerencia.sap.dockWidgets.copyWorkUnit  import CopyWorkUnit

class DockDirector:

    #interface
    def constructSapManagementDock(self, dockSapBuilder, sapCtrl):
        users = sapCtrl.getSapUsers()
        databases = sapCtrl.getSapDatabases()
        inputGroups = sapCtrl.getSapInputGroups()
        #management project tab
        for functionWidget in [
                {
                    "name" : 'Abrir atividade',
                    "widget" : OpenActivity(sapCtrl)
                },
                {
                    "name" : 'Abrir atividade do operador',
                    "widget" : OpenNextActivityByUser(users, sapCtrl)
                },
                {
                    "name" : 'Bloquear unidades de trabalho',
                    "widget" : LockWorkspace(sapCtrl)
                },
                {
                    "name" : 'Desbloquear unidades de trabalho',
                    "widget" : UnlockWorkspace(sapCtrl)
                },
                {
                    "name" : 'Pausar atividades em execução',
                    "widget" : PauseActivity(sapCtrl)
                },
                {
                    "name" : 'Reiniciar atividades em execução ou pausadas',
                    "widget" : RestartActivity(sapCtrl)
                },
                {
                    "name" : 'Definir atividades prioritárias',
                    "widget" : SetPriorityActivity(users, sapCtrl)
                },
                {
                    "name" : 'Definir atividades prioritárias de grupo',
                    "widget" : CreatePriorityGroupActivity(sapCtrl)
                },
                {
                    "name" : 'Avançar atividades para próxima etapa',
                    "widget" : AdvanceActivityToNextStep(sapCtrl)
                },
                {
                    "name" : 'Retornar atividades para etapa anterior',
                    "widget" : ReturnActivityToPreviousStep(sapCtrl)
                },
                {
                    "name" : 'Preencher observações',
                    "widget" : FillComments(sapCtrl)
                },
                {
                    "name" : 'Carregar camadas de acompanhamento',
                    "widget" : LoadLayersQgisProject(sapCtrl)
                },
                {
                    "name" : 'Criar telas de acompanhamento',
                    "widget" : CreateScreens(sapCtrl)
                },
                {
                    "name" : 'Redefinir permissões',
                    "widget" : ResetPrivileges(sapCtrl)
                },
                {
                    "name" : 'Revogar permissões',
                    "widget" : RevokePrivileges(databases, sapCtrl)
                },
                {
                    "name" : 'Copiar configurações para modo local',
                    "widget" : CopySetupToLocalMode(databases, sapCtrl)
                },
                {
                    "name" : 'Atualizar atividades bloqueadas',
                    "widget" : UpdateBlockedActivities(sapCtrl)
                }
            ]:
            dockSapBuilder.addProjectManagementWidget(functionWidget['name'], functionWidget['widget'])
        #creation project tab
        for functionWidget in [
                {
                    "name" : 'Gerar projeto de acompanhamento',
                    "widget" : DownloadQgisProject(sapCtrl)
                },
                {
                    "name" : 'Gerenciador de estilos',
                    "widget" : ManagementStyles(sapCtrl)
                },
                {
                    "name" : 'Gerenciador de modelos',
                    "widget" : ManagementModels(sapCtrl)
                },
                {
                    "name" : 'Gerenciador de regras',
                    "widget" : ManagementRules(sapCtrl)
                },
                {
                    "name" : 'Configurar servidores do gerenciador FME',
                    "widget" : SetupFmeServers(sapCtrl)
                },
                {
                    "name" : 'Configurar perfil de rotinas FME',
                    "widget" : SetupFmeProfiles(sapCtrl)
                },
                {
                    "name" : 'Gera unidades de trabalho',
                    "widget" : GeneratesWorkUnit(sapCtrl.getQgisComboBoxPolygonLayer(), sapCtrl)
                },
                {
                    "name" : 'Carregar unidades de trabalho',
                    "widget" : LoadWorkUnit(sapCtrl.getQgisComboBoxPolygonLayer(), sapCtrl)
                },
                {
                    "name" : 'Copiar unidades de trabalho',
                    "widget" : CopyWorkUnit(sapCtrl)
                },
                {
                    "name" : 'Adicionar nova revisão',
                    "widget" : AddNewRevision(sapCtrl)
                },
                {
                    "name" : 'Adicionar nova revisão/correção',
                    "widget" : AddNewRevisionCorrection(sapCtrl)
                },
                {
                    "name" : 'Criar atividades',
                    "widget" : CreateActivities(sapCtrl)
                },
                {
                    "name" : 'Deletar atividades',
                    "widget" : DeleteActivities(sapCtrl)
                },
                {
                    "name" : 'Importar usuários',
                    "widget" : ImportUsersAuthService(sapCtrl)
                },
                {
                    "name" : 'Sincronizar informações de usuários',
                    "widget" : SynchronizeUserInformation(sapCtrl)
                },
                {
                    "name" : 'Modificar permissões usuários',
                    "widget" : ManagementUsersPrivileges(sapCtrl)
                },
                {
                    "name" : 'Importar camadas',
                    "widget" : ImportLayers(sapCtrl)
                },
                {
                    "name" : 'Configurar camadas',
                    "widget" : SetupLayers(sapCtrl)
                },
                {
                    "name" : 'Alterar lote',
                    "widget" : AlterLot(sapCtrl)
                },
                {
                    "name" : 'Criar produtos',
                    "widget" : CreateProduct(sapCtrl.getQgisComboBoxPolygonLayer(), sapCtrl)
                },
                {
                    "name" : 'Associar insumos',
                    "widget" : AssociateInputs(inputGroups, sapCtrl)
                },
                {
                    "name" : 'Deletar insumos associados',
                    "widget" : DeleteAssociatedInputs(inputGroups, sapCtrl)
                },
                {
                    "name" : 'Deletar unidades de trabalho',
                    "widget" : DeleteWorkUnits(sapCtrl)
                },
                {
                    "name" : 'Deletar revisão e correção',
                    "widget" : DeleteRevisionCorrection(sapCtrl)
                }
            ]:
            dockSapBuilder.addProjectCreationWidget(functionWidget['name'], functionWidget['widget'])
        #danger zone tab
        
        for functionWidget in [
                {
                    "name" : 'Remover feições em área',
                    "widget" : DeleteFeatures(sapCtrl)
                },
                {
                    "name" : 'Limpar atividades de usuário',
                    "widget" : ClearUserActivities(users, sapCtrl)
                }
            ]:
            dockSapBuilder.addDangerZoneWidget(functionWidget['name'], functionWidget['widget'])
            
            