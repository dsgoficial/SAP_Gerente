from Ferramentas_Gerencia.widgets.mMenu  import MMenu

class MMenuSingleton:

    instance = None

    @staticmethod
    def getInstance(*args):
        if not MMenuSingleton.instance:
            MMenuSingleton.instance = MMenu(*args)
        return MMenuSingleton.instance