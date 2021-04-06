from Ferramentas_Gerencia.widgets.addRuleProfileForm  import AddRuleProfileForm

class AddRuleProfileFormSingleton:

    addRuleProfileForm = None

    @staticmethod
    def getInstance(parent):
        if not AddRuleProfileFormSingleton.addRuleProfileForm:
            AddRuleProfileFormSingleton.addRuleProfileForm = AddRuleProfileForm(parent)
        return AddRuleProfileFormSingleton.addRuleProfileForm