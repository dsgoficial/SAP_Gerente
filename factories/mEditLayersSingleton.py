from Ferramentas_Gerencia.widgets.mEditLayers  import MEditLayers

class MEditLayersSingleton:

    mEditLayers = None

    @staticmethod
    def getInstance(controller):
        if not MEditLayersSingleton.mEditLayers:
            MEditLayersSingleton.mEditLayers = MEditLayers(controller)
        return MEditLayersSingleton.mEditLayers