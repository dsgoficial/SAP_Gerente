from Ferramentas_Gerencia.widgets.addModelProfileForm  import AddModelProfileForm

class AddModelProfileFormSingleton:

    addModelProfileForm = None

    @staticmethod
    def getInstance(parent):
        if not AddModelProfileFormSingleton.addModelProfileForm:
            AddModelProfileFormSingleton.addModelProfileForm = AddModelProfileForm(parent)
        return AddModelProfileFormSingleton.addModelProfileForm