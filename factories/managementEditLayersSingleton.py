from Ferramentas_Gerencia.widgets.managementEditLayers  import ManagementEditLayers

class ManagementEditLayersSingleton:

    managementEditLayers = None

    @staticmethod
    def getInstance(controller):
        if not ManagementEditLayersSingleton.managementEditLayers:
            ManagementEditLayersSingleton.managementEditLayers = ManagementEditLayers(controller)
        return ManagementEditLayersSingleton.managementEditLayers