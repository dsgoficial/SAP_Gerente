from Ferramentas_Gerencia.sap.models.functionsSettings.interface.IFunctionSettings import IFunctionSettings

class AddNewRevisionCorrectionSettings(IFunctionSettings):

    def getLayersOptions(self):
        return [
            {
                "layerName" : "atividades_em_execucao",
                "fieldName" : "unidade_trabalho_id",
                "allSelection" : True,
                "chooseAttribute": False
            },
            {
                "layerName" : "problema_atividade",
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