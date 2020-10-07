from Ferramentas_Gerencia.dialogs.managementRuleSet import ManagementRuleSet

class ManagementRuleSetSingleton:

    managementRuleSet = None

    @staticmethod
    def getInstance(controller, parent):
        if not ManagementRuleSetSingleton.managementRuleSet:
            ManagementRuleSetSingleton.managementRuleSet = ManagementRuleSet(controller, parent)
        return ManagementRuleSetSingleton.managementRuleSet