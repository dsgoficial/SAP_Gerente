from Ferramentas_Gerencia.widgets.mModels  import MModels

class MModelsSingleton:

    mModels = None

    @staticmethod
    def getInstance(controller):
        if not MModelsSingleton.mModels:
            MModelsSingleton.mModels = MModels(controller)
        return MModelsSingleton.mModels