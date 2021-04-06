from Ferramentas_Gerencia.widgets.managementStyles  import ManagementStyles

class ManagementStylesSingleton:

    managementStyles = None

    @staticmethod
    def getInstance(controller):
        if not ManagementStylesSingleton.managementStyles:
            ManagementStylesSingleton.managementStyles = ManagementStyles(controller)
        return ManagementStylesSingleton.managementStyles