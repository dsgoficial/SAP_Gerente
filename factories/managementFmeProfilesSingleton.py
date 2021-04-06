from Ferramentas_Gerencia.widgets.managementFmeProfiles  import ManagementFmeProfiles

class ManagementFmeProfilesSingleton:

    managementFmeProfiles = None

    @staticmethod
    def getInstance(controller):
        if not ManagementFmeProfilesSingleton.managementFmeProfiles:
            ManagementFmeProfilesSingleton.managementFmeProfiles = ManagementFmeProfiles(controller)
        return ManagementFmeProfilesSingleton.managementFmeProfiles