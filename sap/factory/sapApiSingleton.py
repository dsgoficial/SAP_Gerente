from Ferramentas_Gerencia.sap.api.sapApiHttp import SapApiHttp

class SapApiSingleton:

    sapApi = None

    @staticmethod
    def getInstance():
        if not SapApiSingleton.sapApi:
            SapApiSingleton.sapApi = SapApiHttp()
            return SapApiSingleton.sapApi
        return SapApiSingleton.sapApi