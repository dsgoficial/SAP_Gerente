from Ferramentas_Gerencia.widgets.addStyleProfileForm  import AddStyleProfileForm

class AddStyleProfileFormSingleton:

    addStyleProfileForm = None

    @staticmethod
    def getInstance(parent):
        if not AddStyleProfileFormSingleton.addStyleProfileForm:
            AddStyleProfileFormSingleton.addStyleProfileForm = AddStyleProfileForm(parent)
        return AddStyleProfileFormSingleton.addStyleProfileForm