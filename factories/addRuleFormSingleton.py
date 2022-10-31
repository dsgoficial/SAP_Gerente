from Ferramentas_Gerencia.widgets.addRuleFormV2  import AddRuleFormV2

class AddRuleFormSingleton:

    instance = None

    @staticmethod
    def getInstance(widgetExpression, parent):
        if not AddRuleFormSingleton.instance:
            AddRuleFormSingleton.instance = AddRuleFormV2(parent)
        return AddRuleFormSingleton.instance