from Ferramentas_Gerencia.qgis.pluginsViewManager.pluginsViewManager import PluginsViewManager

class PluginsViewManagerSingleton:

    pluginsViewManager = None

    @staticmethod
    def getInstance():
        if not PluginsViewManagerSingleton.pluginsViewManager:
            PluginsViewManagerSingleton.pluginsViewManager = PluginsViewManager()
        return PluginsViewManagerSingleton.pluginsViewManager