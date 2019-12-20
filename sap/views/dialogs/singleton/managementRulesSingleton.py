from Ferramentas_Gerencia.sap.views.dialogs.managementRules  import ManagementRules

class ManagementRulesSingleton:

    managementRules = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementRulesSingleton.managementRules:
            ManagementRulesSingleton.managementRules = ManagementRules(sapCtrl)
        return ManagementRulesSingleton.managementRules