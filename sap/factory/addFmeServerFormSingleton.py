from Ferramentas_Gerencia.sap.dialogs.addFmeServerForm  import AddFmeServerForm

class AddFmeServerFormSingleton:

    addFmeServerForm = None

    @staticmethod
    def getInstance(parent):
        if not AddFmeServerFormSingleton.addFmeServerForm:
            AddFmeServerFormSingleton.addFmeServerForm = AddFmeServerForm(parent)
        return AddFmeServerFormSingleton.addFmeServerForm