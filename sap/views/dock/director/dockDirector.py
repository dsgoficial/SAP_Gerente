from Ferramentas_Gerencia.sap.views.dockWidgets.addNewRevision  import AddNewRevision
from Ferramentas_Gerencia.sap.views.dockWidgets.addNewRevisionCorrection  import AddNewRevisionCorrection
from Ferramentas_Gerencia.sap.views.dockWidgets.advanceActivityToNextStep  import AdvanceActivityToNextStep
from Ferramentas_Gerencia.sap.views.dockWidgets.createPriorityGroupActivity  import CreatePriorityGroupActivity
from Ferramentas_Gerencia.sap.views.dockWidgets.openNextActivityByUser  import OpenNextActivityByUser
from Ferramentas_Gerencia.sap.views.dockWidgets.fillComments  import FillComments
from Ferramentas_Gerencia.sap.views.dockWidgets.openActivity  import OpenActivity
from Ferramentas_Gerencia.sap.views.dockWidgets.lockWorkspace  import LockWorkspace
from Ferramentas_Gerencia.sap.views.dockWidgets.pauseActivity  import PauseActivity
from Ferramentas_Gerencia.sap.views.dockWidgets.unlockWorkspace  import UnlockWorkspace
from Ferramentas_Gerencia.sap.views.dockWidgets.restartActivity  import RestartActivity
from Ferramentas_Gerencia.sap.views.dockWidgets.setPriorityActivity  import SetPriorityActivity
from Ferramentas_Gerencia.sap.views.dockWidgets.returnActivityToPreviousStep  import ReturnActivityToPreviousStep
from Ferramentas_Gerencia.sap.views.dockWidgets.openManagementStyles  import OpenManagementStyles
from Ferramentas_Gerencia.sap.views.dockWidgets.openManagementModels  import OpenManagementModels
from Ferramentas_Gerencia.sap.views.dockWidgets.openManagementRules  import OpenManagementRules

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
                    "name" : 'Abrir próxima atividade do usuário',
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
                }
            ]:
            dockSapBuilder.addProjectManagementWidget(functionWidget['name'], functionWidget['widget'])
        #creation project tab
        for functionWidget in [
                {
                    "name" : 'Gerenciador de estilos',
                    "widget" : OpenManagementStyles(sapCtrl)
                },
                {
                    "name" : 'Gerenciador de modelos',
                    "widget" : OpenManagementModels(sapCtrl)
                },
                {
                    "name" : 'Gerenciador de regras',
                    "widget" : OpenManagementRules(sapCtrl)
                }
            ]:
            dockSapBuilder.addProjectCreationWidget(functionWidget['name'], functionWidget['widget'])
        #danger zone tab
        for functionWidget in []:
            dockSapBuilder.addDangerZoneWidget(functionWidget['name'], functionWidget['widget'])
            
            