from Ferramentas_Gerencia.sap.views.dialogs.addStyleForm  import AddStyleForm

class AddStyleFormSingleton:

    addStyleForm = None

    @staticmethod
    def getInstance(parent):
        if not AddStyleFormSingleton.addStyleForm:
            AddStyleFormSingleton.addStyleForm = AddStyleForm(parent)
        return AddStyleFormSingleton.addStyleForm