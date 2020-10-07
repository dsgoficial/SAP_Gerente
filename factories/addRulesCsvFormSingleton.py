from Ferramentas_Gerencia.dialogs.addRulesCsvForm  import AddRulesCsvForm

class AddRulesCsvFormSingleton:

    addRulesCsvForm = None

    @staticmethod
    def getInstance(controller, parent):
        if not AddRulesCsvFormSingleton.addRulesCsvForm:
            AddRulesCsvFormSingleton.addRulesCsvForm = AddRulesCsvForm(controller, parent)
        return AddRulesCsvFormSingleton.addRulesCsvForm