from Ferramentas_Gerencia.functionsSettings.functionsSettings  import FunctionsSettings

class FunctionsSettingsSingleton:

    functionsSettings = None

    @staticmethod
    def getInstance():
        if not FunctionsSettingsSingleton.functionsSettings:
            FunctionsSettingsSingleton.functionsSettings = FunctionsSettings()
        return FunctionsSettingsSingleton.functionsSettings