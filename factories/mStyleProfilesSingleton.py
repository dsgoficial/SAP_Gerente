from Ferramentas_Gerencia.widgets.mStyleProfiles  import MStyleProfiles

class MStyleProfilesSingleton:

    mStyleProfiles = None

    @staticmethod
    def getInstance(controller):
        if not MStyleProfilesSingleton.mStyleProfiles:
            MStyleProfilesSingleton.mStyleProfiles = MStyleProfiles(controller)
        return MStyleProfilesSingleton.mStyleProfiles