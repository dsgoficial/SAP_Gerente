from Ferramentas_Gerencia.sap.dialogs.addFmeProfileForm  import AddFmeProfileForm

class AddFmeProfileFormSingleton:

    addFmeProfileForm = None

    @staticmethod
    def getInstance(sapCtrl, parent):
        if not AddFmeProfileFormSingleton.addFmeProfileForm:
            AddFmeProfileFormSingleton.addFmeProfileForm = AddFmeProfileForm(sapCtrl, parent)
        return AddFmeProfileFormSingleton.addFmeProfileForm