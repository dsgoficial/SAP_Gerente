from Ferramentas_Gerencia.widgets.mModelProfiles  import MModelProfiles

class MModelProfilesSingleton:

    mModelProfiles = None

    @staticmethod
    def getInstance(controller):
        if not MModelProfilesSingleton.mModelProfiles:
            MModelProfilesSingleton.mModelProfiles = MModelProfiles(controller)
        return MModelProfilesSingleton.mModelProfiles