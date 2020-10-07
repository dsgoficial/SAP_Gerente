from Ferramentas_Gerencia.dialogs.managementStyles  import ManagementStyles

class ManagementStylesSingleton:

    managementStyles = None

    @staticmethod
    def getInstance(controller):
        if not ManagementStylesSingleton.managementStyles:
            ManagementStylesSingleton.managementStyles = ManagementStyles(controller)
        return ManagementStylesSingleton.managementStyles