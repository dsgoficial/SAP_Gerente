from SAP_Gerente.modules.dsgTools.processingLaunchers.processing import Processing
from qgis import core, gui
import processing
import json

class ExtractSelectedFeatures(Processing):
    
    def __init__(self):
        super(ExtractSelectedFeatures, self).__init__()
        self.processingId = 'native:saveselectedfeatures'
        
    def getParameters(self, parameters):
        return { 'INPUT' : self.getLayerUriFromId(parameters['layerId']), 'OUTPUT' : 'TEMPORARY_OUTPUT' }
