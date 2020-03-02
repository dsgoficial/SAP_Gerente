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
from Ferramentas_Gerencia.sap.dockWidgets.createWorkUnit  import CreateWorkUnit
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

class DockDirector:

    #interface
    def constructSapManagementDock(self, dockSapBuilder, sapCtrl):
        #management project tab
        for functionWidget in [
                {
                    "name" : 'Adicionar nova revisão',
                    "widget" : AddNewRevision(sapCtrl)
                },
                {
                    "name" : 'Adicionar nova revisão/correção',
                    "widget" : AddNewRevisionCorrection(sapCtrl)
                },
                {
                    "name" : 'Avançar atividades para próxima etapa',
                    "widget" : AdvanceActivityToNextStep(sapCtrl)
                },
                {
                    "name" : 'Definir atividades prioritária de grupo',
                    "widget" : CreatePriorityGroupActivity(sapCtrl)
                },
                {
                    "name" : 'Preencher observações',
                    "widget" : FillComments(sapCtrl)
                },
                {
                    "name" : 'Abrir atividade',
                    "widget" : OpenActivity(sapCtrl)
                },
                {
                    "name" : 'Bloquear unidades de trabalho',
                    "widget" : LockWorkspace(sapCtrl)
                },
                {
                    "name" : 'Abrir atividade do operador',
                    "widget" : OpenNextActivityByUser(sapCtrl)
                },
                {
                    "name" : 'Pausar atividades em execução',
                    "widget" : PauseActivity(sapCtrl)
                },
                {
                    "name" : 'Desbloquear unidades de trabalho',
                    "widget" : UnlockWorkspace(sapCtrl)
                },
                {
                    "name" : 'Reiniciar atividades em execução ou pausadas',
                    "widget" : RestartActivity(sapCtrl)
                },
                {
                    "name" : 'Definir atividades prioritária',
                    "widget" : SetPriorityActivity(sapCtrl)
                },
                {
                    "name" : 'Retornar atividades para etapa anterior',
                    "widget" : ReturnActivityToPreviousStep(sapCtrl)
                },
                {
                    "name" : 'Atualizar atividades bloqueadas',
                    "widget" : UpdateBlockedActivities(sapCtrl)
                },
                {
                    "name" : 'Carregar camadas de acompanhamento',
                    "widget" : LoadLayersQgisProject(sapCtrl)
                },
                {
                    "name" : 'Redefinir permissões',
                    "widget" : ResetPrivileges(sapCtrl)
                }
            ]:
            dockSapBuilder.addProjectManagementWidget(functionWidget['name'], functionWidget['widget'])
        #creation project tab
        for functionWidget in [
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
                    "name" : 'Cria unidade de trabalho',
                    "widget" : CreateWorkUnit(sapCtrl)
                }
                ,
                {
                    "name" : 'Projeto de acompanhamento',
                    "widget" : DownloadQgisProject(sapCtrl)
                },
                {
                    "name" : 'Deletar atividades',
                    "widget" : DeleteActivities(sapCtrl)
                },
                {
                    "name" : 'Criar atividades',
                    "widget" : CreateActivities(sapCtrl)
                },
                {
                    "name" : 'Sincronizar informações de usuários',
                    "widget" : SynchronizeUserInformation(sapCtrl)
                },
                {
                    "name" : 'Importar usuários',
                    "widget" : ImportUsersAuthService(sapCtrl)
                },
                {
                    "name" : 'Permissões usuários',
                    "widget" : ManagementUsersPrivileges(sapCtrl)
                }
            ]:
            dockSapBuilder.addProjectCreationWidget(functionWidget['name'], functionWidget['widget'])
        #danger zone tab
        
        for functionWidget in [
                {
                    "name" : 'Remover feições em área',
                    "widget" : DeleteFeatures(sapCtrl)
                }
            ]:
            dockSapBuilder.addDangerZoneWidget(functionWidget['name'], functionWidget['widget'])
            
            