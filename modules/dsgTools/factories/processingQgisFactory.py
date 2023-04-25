from Ferramentas_Gerencia.modules.dsgTools.processingLaunchers.splitPolygons import SplitPolygons
from Ferramentas_Gerencia.modules.dsgTools.processingLaunchers.deaggregator import Deaggregator

class ProcessingQgisFactory:

    def __init__(self):
        super(ProcessingQgisFactory, self).__init__()

    def createProcessing(self, processingName):
        processingNames = {
            'SplitPolygons': SplitPolygons,
            'Deaggregator': Deaggregator
        }
        return processingNames[processingName]()
            