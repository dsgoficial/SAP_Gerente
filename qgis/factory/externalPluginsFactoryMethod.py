from Ferramentas_Gerencia.qgis.externalPlugins.ferramentaProducao  import FerramentaProducao

class ExternalPluginsFactoryMethod:

    def getPlugin(self, pluginName):
        if pluginName == 'ferramentaProducao':
            return FerramentaProducao()
       