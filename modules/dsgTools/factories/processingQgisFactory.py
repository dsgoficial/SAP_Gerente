from Ferramentas_Gerencia.modules.dsgTools.processingLaunchers.splitPolygons import SplitPolygons

class ProcessingQgisFactory:

    def __init__(self):
        super(ProcessingQgisFactory, self).__init__()

    def createProcessing(self, processingName):
        processingNames = {
            'SplitPolygons': SplitPolygons
        }
        return processingNames[processingName]()
            