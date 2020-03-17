from Ferramentas_Gerencia.sap.dialogs.managementFmeProfiles  import ManagementFmeProfiles

class ManagementFmeProfilesSingleton:

    managementFmeProfiles = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementFmeProfilesSingleton.managementFmeProfiles:
            ManagementFmeProfilesSingleton.managementFmeProfiles = ManagementFmeProfiles(sapCtrl)
        return ManagementFmeProfilesSingleton.managementFmeProfiles