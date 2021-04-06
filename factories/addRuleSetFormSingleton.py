from Ferramentas_Gerencia.widgets.addRuleSetForm  import AddRuleSetForm

class AddRuleSetFormSingleton:

    addRuleSetForm = None

    @staticmethod
    def getInstance(parent):
        if not AddRuleSetFormSingleton.addRuleSetForm:
            AddRuleSetFormSingleton.addRuleSetForm = AddRuleSetForm(parent)
        return AddRuleSetFormSingleton.addRuleSetForm