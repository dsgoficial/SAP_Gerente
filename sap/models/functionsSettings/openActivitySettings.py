from Ferramentas_Gerencia.sap.models.functionsSettings.interface.IFunctionSettings import IFunctionSettings

class OpenActivitySettings(IFunctionSettings):

    def getLayersOptions(self):
        return [
            {
                "layerName" : "problema_atividade",
                "fieldName" : "atividade_id",
                "allSelection" : False,
                "chooseAttribute": False
            },
            {
                "layerName" : "atividades_em_execucao",
                "fieldName" : "atividade_id",
                "allSelection" : False,
                "chooseAttribute": False
            },
            {
                "layerName" : "ultimas_atividades_finalizadas",
                "fieldName" : "atividade_id",
                "allSelection" : False,
                "chooseAttribute": False
            },
            {
                "layerName" : "subfase_",
                "fieldName" : "atividade_id",
                "allSelection" : False,
                "chooseAttribute": True
            }
        ]