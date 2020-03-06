from Ferramentas_Gerencia.sap.dialogs.managementEditLayers  import ManagementEditLayers

class ManagementEditLayersSingleton:

    managementEditLayers = None

    @staticmethod
    def getInstance(sapCtrl):
        if not ManagementEditLayersSingleton.managementEditLayers:
            ManagementEditLayersSingleton.managementEditLayers = ManagementEditLayers(sapCtrl)
        return ManagementEditLayersSingleton.managementEditLayers