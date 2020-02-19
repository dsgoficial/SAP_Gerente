from Ferramentas_Gerencia.qgis.widgets.lineEditExpression  import LineEditExpression

class WidgetsFactoryMethod:

    def getWidget(self, widgetName):
        if widgetName == 'lineEditExpression':
            return LineEditExpression()
       