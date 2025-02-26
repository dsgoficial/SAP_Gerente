from SAP_Gerente.modules.dsgTools.processingLaunchers.processing import Processing
from qgis import core, gui
import processing
import json

class GenerateSystematicGridRelatedToLayer(Processing):
    
    def __init__(self):
        super(GenerateSystematicGridRelatedToLayer, self).__init__()
        self.processingId = 'dsgtools:createframeswithconstraintalgorithm'
        
    def getParameters(self, parameters):
        return {
            'INPUT' : self.getLayerUriFromId(parameters['layerId']),
            'STOP_SCALE': parameters['scale'],
            'XSUBDIVISIONS': None,
            'YSUBDIVISIONS': None,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }