from Ferramentas_Gerencia.rules.rules  import Rules

class RulesSingleton:

    rules = None

    @staticmethod
    def getInstance():
        if not RulesSingleton.rules:
            RulesSingleton.rules = Rules()
        return RulesSingleton.rules