from Ferramentas_Gerencia.sap.models.functionsSettings.interface.IFunctionSettings import IFunctionSettings

class LockWorkspaceSettings(IFunctionSettings):

    def getLayersOptions(self):
        return [
            {
                "layerName" : "problema_atividade",
                "fieldName" : "unidade_trabalho_id",
                "allSelection" : True,
                "chooseAttribute": False
            },
            {
                "layerName" : "atividades_em_execucao",
                "fieldName" : "unidade_trabalho_id",
                "allSelection" : True,
                "chooseAttribute": False
            },
            {
                "layerName" : "ultimas_atividades_finalizadas",
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