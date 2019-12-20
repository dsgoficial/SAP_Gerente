from Ferramentas_Gerencia.qgis.views.widgets.lineEditExpression  import LineEditExpression

class WidgetsFactory:

    def getWidget(self, widgetName):
        if widgetName == 'lineEditExpression':
            return LineEditExpression()
       