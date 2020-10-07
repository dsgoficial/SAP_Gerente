from Ferramentas_Gerencia.dialogs.managementFmeServers  import ManagementFmeServers

class ManagementFmeServersSingleton:

    managementFmeServers = None

    @staticmethod
    def getInstance(controller):
        if not ManagementFmeServersSingleton.managementFmeServers:
            ManagementFmeServersSingleton.managementFmeServers = ManagementFmeServers(controller)
        return ManagementFmeServersSingleton.managementFmeServers