from Ferramentas_Gerencia.sap.models.api.apiSapHttp import ApiSapHttp

class ApiSapSingleton:

    apiSap = None

    @staticmethod
    def getInstance():
        if not ApiSapSingleton.apiSap:
            ApiSapSingleton.apiSap = ApiSapHttp()
            return ApiSapSingleton.apiSap
        return ApiSapSingleton.apiSap