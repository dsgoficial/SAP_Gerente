from Ferramentas_Gerencia.widgets.mRuleSet import MRuleSet

class MRuleSetSingleton:

    mRuleSet = None

    @staticmethod
    def getInstance(controller, parent):
        if not MRuleSetSingleton.mRuleSet:
            MRuleSetSingleton.mRuleSet = MRuleSet(controller, parent)
        return MRuleSetSingleton.mRuleSet