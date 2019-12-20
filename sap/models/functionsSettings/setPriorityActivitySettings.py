from Ferramentas_Gerencia.sap.models.functionsSettings.interface.IFunctionSettings import IFunctionSettings

class SetPriorityActivitySettings(IFunctionSettings):

    def getLayersOptions(self):
        return [
            {
                "layerName" : "subfase_",
                "fieldName" : "atividade_id",
                "allSelection" : True,
                "chooseAttribute": True
            }
        ]