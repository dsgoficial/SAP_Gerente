from Ferramentas_Gerencia.sap.dialogs.addRulesCsvForm  import AddRulesCsvForm

class AddRulesCsvFormSingleton:

    addRulesCsvForm = None

    @staticmethod
    def getInstance(sapCtrl, parent):
        if not AddRulesCsvFormSingleton.addRulesCsvForm:
            AddRulesCsvFormSingleton.addRulesCsvForm = AddRulesCsvForm(sapCtrl, parent)
        return AddRulesCsvFormSingleton.addRulesCsvForm