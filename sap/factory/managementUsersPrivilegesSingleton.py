from Ferramentas_Gerencia.sap.dialogs.managementUsersPrivileges  import ManagementUsersPrivileges

class ManagementUsersPrivilegesSingleton:

    managementUsersPrivileges = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementUsersPrivilegesSingleton.managementUsersPrivileges:
            ManagementUsersPrivilegesSingleton.managementUsersPrivileges = ManagementUsersPrivileges(sapCtrl)
        return ManagementUsersPrivilegesSingleton.managementUsersPrivileges