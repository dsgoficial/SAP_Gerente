from Ferramentas_Gerencia.widgets.managementModelProfiles  import ManagementModelProfiles

class ManagementModelProfilesSingleton:

    managementModelProfiles = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementModelProfilesSingleton.managementModelProfiles:
            ManagementModelProfilesSingleton.managementModelProfiles = ManagementModelProfiles(sapCtrl)
        return ManagementModelProfilesSingleton.managementModelProfiles