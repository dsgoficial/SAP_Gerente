from Ferramentas_Gerencia.qgis.interfaces.IQgisCtrl import IQgisCtrl

from Ferramentas_Gerencia.qgis.factory.qgisApiBuilder import QgisApiBuilder
from Ferramentas_Gerencia.qgis.factory.qgisApiDirector import QgisApiDirector

from Ferramentas_Gerencia.qgis.factory.pluginsManagerSingleton import PluginsManagerSingleton
from Ferramentas_Gerencia.qgis.factory.selectFieldOptionSingleton import SelectFieldOptionSingleton
from Ferramentas_Gerencia.qgis.factory.widgetsFactoryMethod import WidgetsFactoryMethod
from Ferramentas_Gerencia.qgis.factory.mapToolsFactoryMethod import MapToolsFactoryMethod

class QgisCtrl(IQgisCtrl):

    def __init__(self, iface):
        super(QgisCtrl, self).__init__()
        self.iface = iface
        self.apiQGis = self.loadApiQgis()
        self.selectFieldView = SelectFieldOptionSingleton.getInstance()
        self.pluginViewQgis = PluginsManagerSingleton.getInstance()

    def loadApiQgis(self):
        apiGisDirector = QgisApiDirector()
        apiQgisBuilder = QgisApiBuilder()
        apiGisDirector.constructQgisApi(apiQgisBuilder)
        return apiQgisBuilder.getResult()

    def setProjectVariable(self, key, value):
        self.apiQGis.getStorages().setProjectVariable(key, value)

    def getProjectVariable(self, key):
        return self.apiQGis.getStorages().getProjectVariable(key)

    def setSettingsVariable(self, key, value):
        self.apiQGis.getStorages().setSettingsVariable(key, value)

    def getSettingsVariable(self, key):
        return self.apiQGis.getStorages().getSettingsVariable(key)

    def getVersion(self):
        return self.apiQGis.getVersion()
    
    def getPluginsVersions(self):
        return self.apiQGis.getPluginsVersions()

    def addDockWidget(self, dockWidget):
        self.pluginViewQgis.addDockWidget(dockWidget)

    def removeDockWidget(self, dockWidget):
        self.pluginViewQgis.removeDockWidget(dockWidget)

    def getFieldValuesFromLayer(self, layerName, fieldName, allSelection, chooseAttribute):
        layers = self.apiQGis.getLayers()
        if not layers.isActiveLayer(layerName):
            return []
        if not(allSelection) and len(layers.getActiveLayerSelections()) > 1:
            raise Exception("Seleciona apenas uma feição!")
        selectedFeatures = layers.getActiveLayerSelections()
        if chooseAttribute:
            fieldsNames = layers.getFieldsNamesFromSelection(filterText=fieldName)
            fieldName = self.selectFieldView.chooseField(fieldsNames)
        if not fieldName:
            return []
        return layers.getFieldValuesFromSelections(fieldName)

    def getQmlStyleFromLayersTreeSelection(self):
        layers = self.apiQGis.getLayers().getLayersTreeSelection()
        stylesData = self.apiQGis.getStyles().getQmlStyleFromLayers(layers)
        return stylesData

    def applyStylesOnLayers(self, stylesData):
        for styleData in stylesData:
            layers = self.apiQGis.getLayers().findVectorLayer(
                    styleData['f_table_schema'],
                    styleData['f_table_name']
                )
            if not layers:
                continue
            for layer in layers:
                self.apiQGis.getStyles().setQmlStyleToLayer(
                    layer, 
                    styleData['styleqml']
                )

    def getWidgetExpression(self):
        return WidgetsFactoryMethod().getWidget('lineEditExpression')

    def activeMapToolByToolName(self, toolName):
        self.mapTool = MapToolsFactoryMethod.getMapTool(toolName)
        self.mapTool.start()