from qgis.gui import QgsMapLayerComboBox
from Ferramentas_Gerencia.modules.qgis.interfaces.IComboBoxLayer import IComboBoxLayer

class ComboBoxMapLayer(QgsMapLayerComboBox, IComboBoxLayer):
    
    def __init__(self, transformGeometryCrsFunction):
        super(ComboBoxMapLayer, self).__init__()
        self.transformGeometryCrsFunction = transformGeometryCrsFunction

    def getCurrentLayerFields(self):
        if not self.currentLayer():
            return []
        return self.currentLayer().fields().names()