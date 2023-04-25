from Ferramentas_Gerencia.modules.dsgTools.processingLaunchers.processing import Processing
from qgis import core, gui
import processing
import json

class Deaggregator(Processing):
    
    def __init__(self):
        super(Deaggregator, self).__init__()
        self.processingId = 'dsgtools:deaggregategeometries'
        
    def getParameters(self, parameters):
        return {
            'INPUT' : self.getLayerUriFromId(parameters['layerId']),
            'SELECTED': False,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }