from Ferramentas_Gerencia.widgets.managementRuleProfiles  import ManagementRuleProfiles

class ManagementRuleProfilesSingleton:

    managementRuleProfiles = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementRuleProfilesSingleton.managementRuleProfiles:
            ManagementRuleProfilesSingleton.managementRuleProfiles = ManagementRuleProfiles(sapCtrl)
        return ManagementRuleProfilesSingleton.managementRuleProfiles