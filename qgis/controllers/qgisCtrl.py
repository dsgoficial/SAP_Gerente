from Ferramentas_Gerencia.qgis.controllers.interface.gisCtrlInterface import GisCtrlInterface

from Ferramentas_Gerencia.qgis.models.api.builder.apiQgisBuilder import ApiQgisBuilder
from Ferramentas_Gerencia.qgis.models.api.director.apiGisDirector import ApiGisDirector

from Ferramentas_Gerencia.qgis.views.plugins.singleton.pluginViewQgisSingleton import PluginViewQgisSingleton
from Ferramentas_Gerencia.qgis.views.dialogs.singleton.selectFieldOptionQgisSingleton import SelectFieldOptionQgisSingleton
from Ferramentas_Gerencia.qgis.views.widgets.factoryMethod.widgetsFactory import WidgetsFactory

class QgisCtrl(GisCtrlInterface):

    def __init__(self):
        self.apiQGis = self.loadApiQgis()
        self.selectFieldView = SelectFieldOptionQgisSingleton.getInstance()
        self.pluginViewQgis = PluginViewQgisSingleton.getInstance()

    def loadApiQgis(self):
        apiGisDirector = ApiGisDirector()
        apiQgisBuilder = ApiQgisBuilder()
        apiGisDirector.constructApiQgis(apiQgisBuilder)
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
        layers = self.apiQGis.getlayers()
        if not layers.isActiveLayer(layerName):
            return []
        if not(allSelection) and len(layers.getActiveLayerSelections()) > 1:
            raise Exception("Seleciona apenas uma feição!")
        selectedFeatures = layers.getActiveLayerSelections()
        if chooseAttribute:
            fieldsNames = layers.getFieldsNamesFromSelection(filterText=fieldName)
            fieldName = self.selectFieldView.chooseField(fieldsNames)
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
        return WidgetsFactory().getWidget('lineEditExpression')