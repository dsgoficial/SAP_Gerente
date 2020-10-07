from Ferramentas_Gerencia.dialogs.managementModels  import ManagementModels

class ManagementModelsSingleton:

    managementModels = None

    @staticmethod
    def getInstance(controller):
        if not ManagementModelsSingleton.managementModels:
            ManagementModelsSingleton.managementModels = ManagementModels(controller)
        return ManagementModelsSingleton.managementModels