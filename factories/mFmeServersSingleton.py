from Ferramentas_Gerencia.widgets.mFmeServers  import MFmeServers

class MFmeServersSingleton:

    mFmeServers = None

    @staticmethod
    def getInstance(controller):
        if not MFmeServersSingleton.mFmeServers:
            MFmeServersSingleton.mFmeServers = MFmeServers(controller)
        return MFmeServersSingleton.mFmeServers