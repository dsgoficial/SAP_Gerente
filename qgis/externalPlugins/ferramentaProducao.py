from qgis.utils import plugins, iface

from Ferramentas_Gerencia.qgis.interfaces.IPlugin import IPlugin

class FerramentaProducao(IPlugin):

    def __init__(self):
        super(FerramentaProducao, self).__init__()

    def run(self, activityData):
        prodTools = plugins['Ferramentas_Producao']
        prodTools.sap.load_sap_activity_from_data(activityData)