from Ferramentas_Gerencia.dialogs.addFmeProfileForm  import AddFmeProfileForm

class AddFmeProfileFormSingleton:

    addFmeProfileForm = None

    @staticmethod
    def getInstance(controller, parent):
        if not AddFmeProfileFormSingleton.addFmeProfileForm:
            AddFmeProfileFormSingleton.addFmeProfileForm = AddFmeProfileForm(controller, parent)
        return AddFmeProfileFormSingleton.addFmeProfileForm