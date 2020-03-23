from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel

class ComboBoxPolygonLayer(QgsMapLayerComboBox):
    
    def __init__(self):
        super(ComboBoxPolygonLayer, self).__init__()
        self.setFilters(QgsMapLayerProxyModel.PolygonLayer)