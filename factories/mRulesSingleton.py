from Ferramentas_Gerencia.widgets.mRules  import MRules

class MRulesSingleton:

    mRules = None

    @staticmethod
    def getInstance(controller, sapCtrl):
        if not MRulesSingleton.mRules:
            MRulesSingleton.mRules = MRules(controller, sapCtrl)
        return MRulesSingleton.mRules