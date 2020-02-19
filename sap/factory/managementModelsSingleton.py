from Ferramentas_Gerencia.sap.dialogs.managementModels  import ManagementModels

class ManagementModelsSingleton:

    managementModels = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementModelsSingleton.managementModels:
            ManagementModelsSingleton.managementModels = ManagementModels(sapCtrl)
        return ManagementModelsSingleton.managementModels