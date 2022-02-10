from Ferramentas_Gerencia.widgets.mImportLayers  import MImportLayers

class MImportLayersSingleton:

    mImportLayers = None

    @staticmethod
    def getInstance(controller):
        if not MImportLayersSingleton.mImportLayers:
            MImportLayersSingleton.mImportLayers = MImportLayers(controller)
        return MImportLayersSingleton.mImportLayers