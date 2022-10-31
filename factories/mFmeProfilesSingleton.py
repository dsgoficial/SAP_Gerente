from Ferramentas_Gerencia.widgets.mFmeProfiles  import MFmeProfiles

class MFmeProfilesSingleton:

    instance = None

    @staticmethod
    def getInstance(controller):
        if not MFmeProfilesSingleton.instance:
            MFmeProfilesSingleton.instance = MFmeProfiles(controller)
        return MFmeProfilesSingleton.instance