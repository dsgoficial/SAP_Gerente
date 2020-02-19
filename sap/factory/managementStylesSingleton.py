from Ferramentas_Gerencia.sap.dialogs.managementStyles  import ManagementStyles

class ManagementStylesSingleton:

    managementStyles = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementStylesSingleton.managementStyles:
            ManagementStylesSingleton.managementStyles = ManagementStyles(sapCtrl)
        return ManagementStylesSingleton.managementStyles