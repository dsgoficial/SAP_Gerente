from Ferramentas_Gerencia.widgets.mMenuProfile  import MMenuProfile

class MMenuProfileSingleton:

    instance = None

    @staticmethod
    def getInstance(*args):
        if not MMenuProfileSingleton.instance:
            MMenuProfileSingleton.instance = MMenuProfile(*args)
        return MMenuProfileSingleton.instance