from Ferramentas_Gerencia.sap.models.functionsSettings.addNewRevisionSettings  import AddNewRevisionSettings
from Ferramentas_Gerencia.sap.models.functionsSettings.addNewRevisionCorrectionSettings import AddNewRevisionCorrectionSettings
from Ferramentas_Gerencia.sap.models.functionsSettings.advanceActivityToNextStepSettings import AdvanceActivityToNextStepSettings
from Ferramentas_Gerencia.sap.models.functionsSettings.createPriorityGroupActivitySettings import CreatePriorityGroupActivitySettings
from Ferramentas_Gerencia.sap.models.functionsSettings.openNextActivityByUserSettings import OpenNextActivityByUserSettings
from Ferramentas_Gerencia.sap.models.functionsSettings.fillCommentsSettings import FillCommentsSettings
from Ferramentas_Gerencia.sap.models.functionsSettings.openActivitySettings import OpenActivitySettings
from Ferramentas_Gerencia.sap.models.functionsSettings.lockWorkspaceSettings import LockWorkspaceSettings
from Ferramentas_Gerencia.sap.models.functionsSettings.pauseActivitySettings import PauseActivitySettings
from Ferramentas_Gerencia.sap.models.functionsSettings.unlockWorkspaceSettings import UnlockWorkspaceSettings
from Ferramentas_Gerencia.sap.models.functionsSettings.restartActivitySettings import RestartActivitySettings
from Ferramentas_Gerencia.sap.models.functionsSettings.setPriorityActivitySettings import SetPriorityActivitySettings
from Ferramentas_Gerencia.sap.models.functionsSettings.returnActivityToPreviousStepSettings import ReturnActivityToPreviousStepSettings

class FunctionsSettingsFactory:

    def getFunctionSettings(self, functionName):
        if functionName == 'addNewRevision':
            return AddNewRevisionSettings()
        elif functionName == 'addNewRevisionCorrection':
            return AddNewRevisionCorrectionSettings()
        elif functionName == 'advanceActivityToNextStep':
            return AdvanceActivityToNextStepSettings()
        elif functionName == 'createPriorityGroupActivity':
            return CreatePriorityGroupActivitySettings()
        elif functionName == 'openNextActivityByUserSettings':
            return OpenNextActivityByUserSettings()
        elif functionName == 'fillCommentsSettings':
            return FillCommentsSettings()
        elif functionName == 'openActivitySettings':
            return OpenActivitySettings()
        elif functionName == 'lockWorkspaceSettings':
            return LockWorkspaceSettings()
        elif functionName == 'lockWorkspaceSettings':
            return LockWorkspaceSettings()
        elif functionName == 'pauseActivitySettings':
            return PauseActivitySettings()
        elif functionName == 'unlockWorkspaceSettings':
            return UnlockWorkspaceSettings()
        elif functionName == 'restartActivitySettings':
            return RestartActivitySettings()
        elif functionName == 'setPriorityActivitySettings':
            return SetPriorityActivitySettings()
        elif functionName == 'returnActivityToPreviousStepSettings':
            return ReturnActivityToPreviousStepSettings()