from Ferramentas_Gerencia.sap.dialogs.managementFmeServers  import ManagementFmeServers

class ManagementFmeServersSingleton:

    managementFmeServers = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementFmeServersSingleton.managementFmeServers:
            ManagementFmeServersSingleton.managementFmeServers = ManagementFmeServers(sapCtrl)
        return ManagementFmeServersSingleton.managementFmeServers