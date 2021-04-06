from Ferramentas_Gerencia.widgets.managementImportLayers  import ManagementImportLayers

class ManagementImportLayersSingleton:

    managementImportLayers = None

    @staticmethod
    def getInstance(controller):
        if not ManagementImportLayersSingleton.managementImportLayers:
            ManagementImportLayersSingleton.managementImportLayers = ManagementImportLayers(controller)
        return ManagementImportLayersSingleton.managementImportLayers