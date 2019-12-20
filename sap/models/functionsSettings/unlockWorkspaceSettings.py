from Ferramentas_Gerencia.sap.models.functionsSettings.interface.IFunctionSettings import IFunctionSettings

class UnlockWorkspaceSettings(IFunctionSettings):

    def getLayersOptions(self):
        return [
            {
                "layerName" : "subfase_",
                "fieldName" : "atividade_id",
                "allSelection" : True,
                "chooseAttribute": True
            }
        ]