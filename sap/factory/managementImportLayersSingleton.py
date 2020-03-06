from Ferramentas_Gerencia.sap.dialogs.managementImportLayers  import ManagementImportLayers

class ManagementImportLayersSingleton:

    managementImportLayers = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementImportLayersSingleton.managementImportLayers:
            ManagementImportLayersSingleton.managementImportLayers = ManagementImportLayers(sapCtrl)
        return ManagementImportLayersSingleton.managementImportLayers