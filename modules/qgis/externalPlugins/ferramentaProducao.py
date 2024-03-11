from qgis.utils import plugins, iface

from SAP_Gerente.modules.qgis.interfaces.IPlugin import IPlugin

class FerramentaProducao(IPlugin):

    def __init__(self):
        super(FerramentaProducao, self).__init__()

    def run(self, sapCtrl):
        prodTools = plugins['SAP_Gerente']
        prodTools.startPluginExternally(sapCtrl)