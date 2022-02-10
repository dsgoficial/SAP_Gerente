from Ferramentas_Gerencia.widgets.mRules  import MRules

class MRulesSingleton:

    mRules = None

    @staticmethod
    def getInstance(controller):
        if not MRulesSingleton.mRules:
            MRulesSingleton.mRules = MRules(controller)
        return MRulesSingleton.mRules