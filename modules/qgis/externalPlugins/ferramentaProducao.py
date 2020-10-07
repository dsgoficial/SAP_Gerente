from qgis.utils import plugins, iface

from Ferramentas_Gerencia.modules.qgis.interfaces.IPlugin import IPlugin

class FerramentaProducao(IPlugin):

    def __init__(self):
        super(FerramentaProducao, self).__init__()

    def run(self, sapCtrl):
        prodTools = plugins['Ferramentas_Producao']
        prodTools.startPluginExternally(sapCtrl)