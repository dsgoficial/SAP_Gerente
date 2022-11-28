from Ferramentas_Gerencia.widgets.addStyleProfileForm  import AddStyleProfileForm

class AddStyleProfileFormSingleton:

    addStyleProfileForm = None

    @staticmethod
    def getInstance(*args):
        if not AddStyleProfileFormSingleton.addStyleProfileForm:
            AddStyleProfileFormSingleton.addStyleProfileForm = AddStyleProfileForm(*args)
        return AddStyleProfileFormSingleton.addStyleProfileForm