from Ferramentas_Gerencia.widgets.addRulesCsvForm  import AddRulesCsvForm

class AddRulesCsvFormSingleton:

    addRulesCsvForm = None

    @staticmethod
    def getInstance(controller, parent):
        if not AddRulesCsvFormSingleton.addRulesCsvForm:
            AddRulesCsvFormSingleton.addRulesCsvForm = AddRulesCsvForm(controller, parent)
        return AddRulesCsvFormSingleton.addRulesCsvForm