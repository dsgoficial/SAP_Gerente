from qgis.gui import QgsMapLayerComboBox

class ComboBoxMapLayer(QgsMapLayerComboBox):
    
    def __init__(self):
        super(ComboBoxMapLayer, self).__init__()