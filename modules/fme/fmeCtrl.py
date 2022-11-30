from Ferramentas_Gerencia.modules.fme.interfaces.IFmeCtrl import IFmeCtrl
from Ferramentas_Gerencia.modules.fme.factories.fmeApiSingleton import FmeApiSingleton

class FmeCtrl(IFmeCtrl):

    def __init__(self):
        super(FmeCtrl, self).__init__()

    def getRoutines(self, server):
        fmeApi = FmeApiSingleton.getInstance()
        fmeApi.setServer(server)
        return fmeApi.getRoutines()