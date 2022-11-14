from Ferramentas_Gerencia.widgets.mStyles  import MStyles

class MStylesSingleton:

    mStyles = None

    @staticmethod
    def getInstance(*args):
        if not MStylesSingleton.mStyles:
            MStylesSingleton.mStyles = MStyles(*args)
        return MStylesSingleton.mStyles