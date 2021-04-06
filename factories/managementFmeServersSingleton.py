from Ferramentas_Gerencia.widgets.managementFmeServers  import ManagementFmeServers

class ManagementFmeServersSingleton:

    managementFmeServers = None

    @staticmethod
    def getInstance(controller):
        if not ManagementFmeServersSingleton.managementFmeServers:
            ManagementFmeServersSingleton.managementFmeServers = ManagementFmeServers(controller)
        return ManagementFmeServersSingleton.managementFmeServers