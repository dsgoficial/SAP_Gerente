from Ferramentas_Gerencia.widgets.mUsersPrivileges  import MUsersPrivileges

class MUsersPrivilegesSingleton:

    mUsersPrivileges = None

    @staticmethod
    def getInstance(controller):
        if not MUsersPrivilegesSingleton.mUsersPrivileges:
            MUsersPrivilegesSingleton.mUsersPrivileges = MUsersPrivileges(controller)
        return MUsersPrivilegesSingleton.mUsersPrivileges