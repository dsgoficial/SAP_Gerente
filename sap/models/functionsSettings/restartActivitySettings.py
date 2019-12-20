from Ferramentas_Gerencia.sap.models.functionsSettings.interface.IFunctionSettings import IFunctionSettings

class RestartActivitySettings(IFunctionSettings):

    def getLayersOptions(self):
        return [
            {
                "layerName" : "atividades_em_execucao",
                "fieldName" : "unidade_trabalho_id",
                "allSelection" : True,
                "chooseAttribute": False
            },
            {
                "layerName" : "subfase_",
                "fieldName" : "id",
                "allSelection" : True,
                "chooseAttribute": False
            }
        ]