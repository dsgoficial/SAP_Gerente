from SAP_Gerente.modules.fme.api.fmeHttp import FmeHttp

class FmeApiSingleton:

    fmeApi = None

    @staticmethod
    def getInstance():
        if not FmeApiSingleton.fmeApi:
            FmeApiSingleton.fmeApi = FmeHttp()
        return FmeApiSingleton.fmeApi