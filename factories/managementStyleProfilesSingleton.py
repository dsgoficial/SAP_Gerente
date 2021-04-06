from Ferramentas_Gerencia.widgets.managementStyleProfiles  import ManagementStyleProfiles

class ManagementStyleProfilesSingleton:

    managementStyleProfiles = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementStyleProfilesSingleton.managementStyleProfiles:
            ManagementStyleProfilesSingleton.managementStyleProfiles = ManagementStyleProfiles(sapCtrl)
        return ManagementStyleProfilesSingleton.managementStyleProfiles