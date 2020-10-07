from Ferramentas_Gerencia.dialogs.addModelForm  import AddModelForm

class AddModelFormSingleton:

    addModelForm = None

    @staticmethod
    def getInstance(parent):
        if not AddModelFormSingleton.addModelForm:
            AddModelFormSingleton.addModelForm = AddModelForm(parent)
        return AddModelFormSingleton.addModelForm