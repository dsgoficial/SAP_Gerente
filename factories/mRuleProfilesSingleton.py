from Ferramentas_Gerencia.widgets.mRuleProfiles  import MRuleProfiles

class MRuleProfilesSingleton:

    mRuleProfiles = None

    @staticmethod
    def getInstance(controller):
        if not MRuleProfilesSingleton.mRuleProfiles:
            MRuleProfilesSingleton.mRuleProfiles = MRuleProfiles(controller)
        return MRuleProfilesSingleton.mRuleProfiles