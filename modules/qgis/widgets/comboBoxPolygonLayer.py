from SAP_Gerente.modules.qgis.widgets.comboBoxMapLayer import ComboBoxMapLayer
from qgis.core import QgsMapLayerProxyModel

class ComboBoxPolygonLayer(ComboBoxMapLayer):
    
    def __init__(self, transformGeometryCrsFunction):
        super(ComboBoxPolygonLayer, self).__init__(
            transformGeometryCrsFunction=transformGeometryCrsFunction
        )
        self.setFilters(QgsMapLayerProxyModel.PolygonLayer)