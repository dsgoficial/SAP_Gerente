from Ferramentas_Gerencia.qgis.pluginsManager.pluginsManager import PluginsManager

class PluginsManagerSingleton:

    pluginsManager = None

    @staticmethod
    def getInstance():
        if not PluginsManagerSingleton.pluginsManager:
            PluginsManagerSingleton.pluginsManager = PluginsManager()
        return PluginsManagerSingleton.pluginsManager