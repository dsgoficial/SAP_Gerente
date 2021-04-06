from Ferramentas_Gerencia.widgets.managementRules  import ManagementRules

class ManagementRulesSingleton:

    managementRules = None

    @staticmethod
    def getInstance(controller):
        if not ManagementRulesSingleton.managementRules:
            ManagementRulesSingleton.managementRules = ManagementRules(controller)
        return ManagementRulesSingleton.managementRules