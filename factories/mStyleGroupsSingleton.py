from Ferramentas_Gerencia.widgets.mStyleGroups  import MStyleGroups

class MStyleGroupsSingleton:

    instance = None

    @staticmethod
    def getInstance(controller, sapCtrl):
        if not MStyleGroupsSingleton.instance:
            MStyleGroupsSingleton.instance = MStyleGroups(controller, sapCtrl)
        return MStyleGroupsSingleton.instance