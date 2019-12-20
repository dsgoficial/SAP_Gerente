from Ferramentas_Gerencia.sap.models.functionsSettings.interface.IFunctionSettings import IFunctionSettings

class AdvanceActivityToNextStepSettings(IFunctionSettings):

    def getLayersOptions(self):
        return [
            {
                "layerName" : "atividades_em_execucao",
                "fieldName" : "atividade_id",
                "allSelection" : True,
                "chooseAttribute": False
            },
            {
                "layerName" : "problema_atividade",
                "fieldName" : "atividade_id",
                "allSelection" : True,
                "chooseAttribute": False
            },
            {
                "layerName" : "subfase_",
                "fieldName" : "atividade_id",
                "allSelection" : True,
                "chooseAttribute": True
            }
        ]