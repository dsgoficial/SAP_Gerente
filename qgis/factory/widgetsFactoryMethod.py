from Ferramentas_Gerencia.qgis.widgets.lineEditExpression  import LineEditExpression
from Ferramentas_Gerencia.qgis.widgets.comboBoxMapLayer  import ComboBoxMapLayer
from Ferramentas_Gerencia.qgis.widgets.comboBoxPolygonLayer  import ComboBoxPolygonLayer
from Ferramentas_Gerencia.qgis.factory.mapFunctionsFactoryMethod import MapFunctionsFactoryMethod

class WidgetsFactoryMethod:

    def getWidget(self, widgetName):
        if widgetName == 'lineEditExpression':
            return LineEditExpression()
        elif widgetName == 'comboBoxMapLayer':
            return ComboBoxMapLayer(
                transformGeometryCrsFunction=MapFunctionsFactoryMethod.getMapFunctions('transformGeometryCrs')
            )
        elif widgetName == 'comboBoxPolygonLayer':
            return ComboBoxPolygonLayer(
                transformGeometryCrsFunction=MapFunctionsFactoryMethod.getMapFunctions('transformGeometryCrs')
            )
            
       