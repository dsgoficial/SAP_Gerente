from Ferramentas_Gerencia.widgets.mFmeProfiles  import MFmeProfiles

class MFmeProfilesSingleton:

    mFmeProfiles = None

    @staticmethod
    def getInstance(controller):
        if not MFmeProfilesSingleton.mFmeProfiles:
            MFmeProfilesSingleton.mFmeProfiles = MFmeProfiles(controller)
        return MFmeProfilesSingleton.mFmeProfiles