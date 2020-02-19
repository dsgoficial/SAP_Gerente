from Ferramentas_Gerencia.sap.dialogs.managementRuleSet import ManagementRuleSet

class ManagementRuleSetSingleton:

    managementRuleSet = None

    @staticmethod
    def getInstance(sapCtrl, parent):
        if not ManagementRuleSetSingleton.managementRuleSet:
            ManagementRuleSetSingleton.managementRuleSet = ManagementRuleSet(sapCtrl, parent)
        return ManagementRuleSetSingleton.managementRuleSet