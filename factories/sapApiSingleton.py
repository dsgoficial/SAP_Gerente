from Ferramentas_Gerencia.api.sapHttp import SapHttp

class SapApiSingleton:

    sapApi = None

    @staticmethod
    def getInstance():
        if not SapApiSingleton.sapApi:
            SapApiSingleton.sapApi = SapHttp()
            return SapApiSingleton.sapApi
        return SapApiSingleton.sapApi