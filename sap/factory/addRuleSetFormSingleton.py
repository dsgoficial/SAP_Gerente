from Ferramentas_Gerencia.sap.dialogs.addRuleSetForm  import AddRuleSetForm

class AddRuleSetFormSingleton:

    addRuleSetForm = None

    @staticmethod
    def getInstance(parent):
        if not AddRuleSetFormSingleton.addRuleSetForm:
            AddRuleSetFormSingleton.addRuleSetForm = AddRuleSetForm(parent)
        return AddRuleSetFormSingleton.addRuleSetForm