from Ferramentas_Gerencia.qgis.widgets.lineEditExpression  import LineEditExpression
from Ferramentas_Gerencia.qgis.widgets.comboBoxMapLayer  import ComboBoxMapLayer
from Ferramentas_Gerencia.qgis.widgets.comboBoxPolygonLayer  import ComboBoxPolygonLayer

class WidgetsFactoryMethod:

    def getWidget(self, widgetName):
        if widgetName == 'lineEditExpression':
            return LineEditExpression()
        elif widgetName == 'comboBoxMapLayer':
            return ComboBoxMapLayer()
        elif widgetName == 'comboBoxPolygonLayer':
            return ComboBoxPolygonLayer()
            
       