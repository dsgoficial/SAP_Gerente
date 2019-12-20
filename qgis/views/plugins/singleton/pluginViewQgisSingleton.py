from Ferramentas_Gerencia.qgis.views.plugins.pluginViewQgis import PluginViewQgis

class PluginViewQgisSingleton:

    pluginView = None

    @staticmethod
    def getInstance():
        if not PluginViewQgisSingleton.pluginView:
            PluginViewQgisSingleton.pluginView = PluginViewQgis()
        return PluginViewQgisSingleton.pluginView