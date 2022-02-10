from Ferramentas_Gerencia.widgets.mStyles  import MStyles

class MStylesSingleton:

    mStyles = None

    @staticmethod
    def getInstance(controller):
        if not MStylesSingleton.mStyles:
            MStylesSingleton.mStyles = MStyles(controller)
        return MStylesSingleton.mStyles