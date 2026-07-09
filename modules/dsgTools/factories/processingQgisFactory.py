from SAP_Gerente.modules.dsgTools.processingLaunchers.splitPolygons import SplitPolygons
from SAP_Gerente.modules.dsgTools.processingLaunchers.deaggregator import Deaggregator
from SAP_Gerente.modules.dsgTools.processingLaunchers.extractSelectedFeatures import ExtractSelectedFeatures
from SAP_Gerente.modules.dsgTools.processingLaunchers.gridZoneGenerator import GridZoneGenerator

class ProcessingQgisFactory:

    def __init__(self):
        super(ProcessingQgisFactory, self).__init__()

    def createProcessing(self, processingName):
        processingNames = {
            'SplitPolygons': SplitPolygons,
            'Deaggregator': Deaggregator,
            'ExtractSelectedFeatures': ExtractSelectedFeatures,
            'GridZoneGenerator': GridZoneGenerator
        }
        return processingNames[processingName]()
            