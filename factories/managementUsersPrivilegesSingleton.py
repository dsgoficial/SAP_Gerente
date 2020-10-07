from Ferramentas_Gerencia.dialogs.managementUsersPrivileges  import ManagementUsersPrivileges

class ManagementUsersPrivilegesSingleton:

    managementUsersPrivileges = None

    @staticmethod
    def getInstance(controller):
        if not ManagementUsersPrivilegesSingleton.managementUsersPrivileges:
            ManagementUsersPrivilegesSingleton.managementUsersPrivileges = ManagementUsersPrivileges(controller)
        return ManagementUsersPrivilegesSingleton.managementUsersPrivileges