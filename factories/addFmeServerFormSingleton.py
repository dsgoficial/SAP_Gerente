from Ferramentas_Gerencia.widgets.addFmeServerForm  import AddFmeServerForm

class AddFmeServerFormSingleton:

    addFmeServerForm = None

    @staticmethod
    def getInstance(parent):
        if not AddFmeServerFormSingleton.addFmeServerForm:
            AddFmeServerFormSingleton.addFmeServerForm = AddFmeServerForm(parent)
        return AddFmeServerFormSingleton.addFmeServerForm