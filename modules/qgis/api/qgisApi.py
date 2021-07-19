from Ferramentas_Gerencia.modules.qgis.interfaces.IQgisApi import IQgisApi

from qgis import gui, core
from qgis.utils import plugins, iface
from configparser import ConfigParser
from PyQt5.QtWidgets import QAction, QMenu
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
import os

import uuid

class QgisApi(IQgisApi):

    tmpFolderPath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'tmp'
    )

    def __init__(self):
        self.storages = None
        self.layers = None
        self.styles = None

    def addActionDigitizeToolBar(self, action):
        iface.digitizeToolBar().addAction(action)

    def removeActionDigitizeToolBar(self, action):
        iface.digitizeToolBar().removeAction(action)

    def isActiveLayer(self, layerName):
        activeLayer = iface.activeLayer()
        if activeLayer and activeLayer.dataProvider().uri().table():
            return activeLayer and layerName in activeLayer.dataProvider().uri().table()
        return activeLayer and layerName in activeLayer.name()

    def getActiveLayerAttribute(self, featureId, fieldName):
        feat = iface.activeLayer().getFeature(featureId)
        return feat[fieldName]

    def getActiveLayerSelections(self):
        if not iface.activeLayer():
            return []
        return iface.activeLayer().selectedFeatures()

    def getCrsId(self):
        return iface.activeLayer().crs().authid()

    def getActiveLayerAllFeatures(self):
        return iface.activeLayer().getFeatures()

    def isPolygon(self):
        for feat in self.getActiveLayerSelections():
            geom = feat.geometry()
            if not ( geom.wkbType() in [3, 6] ):
                return False
        return True

    def getMainWindow(self):
        return iface.mainWindow()

    def getFieldValuesFromSelections(self, fieldName):
        values = []
        for feature in self.getActiveLayerSelections():
            values.append(feature[fieldName])
        return values

    def getFieldsNamesFromSelection(self, filterText=""):
        if not len(self.getActiveLayerSelections()) > 0:
            return []
        feature = self.getActiveLayerSelections()[0]
        if filterText:
            return [ name for name in feature.fields().names() if filterText in name ]
        return [ name for name in feature.fields().names() ]

    def getLayersTreeSelection(self):
        return iface.layerTreeView().selectedLayers()
    
    def isValidLayer(self, layer, layerSchema, layerName):
        return layer.dataProvider().uri().table() == layerName and layer.dataProvider().uri().schema() == layerSchema

    def findVectorLayer(self, layerSchema, layerName):
        layers = []
        for layer in core.QgsProject.instance().mapLayers().values():
            if self.isValidLayer(layer, layerSchema, layerName):
                layers.append(layer) 
        return layers

    def addLayerGroup(self, groupName, parentGroup=None):
        if parentGroup is None:
            tree = core.QgsProject.instance().layerTreeRoot()
            return tree.addGroup(groupName)
        return parentGroup.addGroup(groupName)

    def getUri(self, dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable):
        return u"""dbname='{}' host={} port={} user='{}' password='{}' key='id' table="{}"."{}" (geom) sql= """.format(
            dbName, 
            dbHost, 
            dbPort, 
            dbUser,
            dbPassword,
            dbSchema,
            dbTable
        )

    def loadPostgresLayer(self, dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable, groupParent=None):
        lyr = core.QgsVectorLayer(
            self.getUri(dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable), 
            dbTable, 
            u"postgres"
        )
        if groupParent is None:
            return self.addLayerOnMap(lyr)
        layer = core.QgsProject.instance().addMapLayer(lyr, False)
        groupParent.addLayer(layer)
        return layer

    def addLayerOnMap(self, layer):
        return core.QgsProject.instance().addMapLayer(layer)

    def addFeature(self, layer, fieldValues, geometry):
        feat = core.QgsFeature()
        feat.setFields(layer.fields())
        feat.setGeometry(geometry)
        for key in fieldValues:
            feat[key] = fieldValues[key]
        provider = layer.dataProvider()
        provider.addFeature(feat)
    
    def getQmlStyleFromLayers(self, layers):
        result = []
        for layer in layers:
            result.append({
                'f_table_schema': layer.dataProvider().uri().schema(),
                'f_table_name': layer.dataProvider().uri().table(),
                'styleqml': self.getQmlStyleFromLayer(layer),
                'stylesld': self.getSldStyleFromLayer(layer),
                'ui': None,
                'f_geometry_column': layer.dataProvider().uri().geometryColumn()
            })
            
        return result

    def getQmlStyleFromLayer(self, layer):
        tmpFilePath = os.path.join( self.tmpFolderPath, '{0}.qml'.format(uuid.uuid4()))
        layer.saveNamedStyle(
            tmpFilePath, 
            categories=core.QgsMapLayer.Symbology | core.QgsMapLayer.Labeling 
        )
        with open(tmpFilePath, "r") as f: 
            qmlData = f.read()
        os.remove(tmpFilePath)
        return qmlData

    def setQmlStyleToLayer(self, layer, qml):
        doc = QDomDocument()
        doc.setContent(qml)
        result = layer.importNamedStyle(doc)
        if not result[0]:
            raise Exception('Erro estilo qml: {0}'.format(result[1]))
        layer.triggerRepaint()

    def getSldStyleFromLayer(self, layer):
        tmpFilePath = os.path.join( self.tmpFolderPath, '{0}.sld'.format(uuid.uuid4()))
        layer.saveSldStyle(
            tmpFilePath
        )
        with open(tmpFilePath, "r") as f:    
            sldData = f.read()
        os.remove(tmpFilePath)
        return sldData

    def setSldStyleToLayer(self, layer, sld):
        tmpFilePath = os.path.join( self.tmpFolderPath, '{0}.sld'.format(uuid.uuid4()))
        with open(tmpFilePath, "w") as f:
            f.write(sld)
        layer.loadSldStyle(tmpFilePath)
        os.remove(tmpFilePath)
        layer.triggerRepaint()
    
    def setProjectVariable(self, key, value):
        chiper_text = base64.b64encode(value.encode('utf-8'))
        core.QgsExpressionContextUtils.setProjectVariable(
            core.QgsProject().instance(), 
            key,
            chiper_text.decode('utf-8')
        )

    def getProjectVariable(self, key):
        current_project  = core.QgsProject().instance()
        chiper_text = core.QgsExpressionContextUtils.projectScope(current_project).variable(
            key
        )
        value = base64.b64decode(str.encode(chiper_text)).decode('utf-8') if chiper_text else ''
        return value

    def setSettingsVariable(self, key, value):
        qsettings = QtCore.QSettings()
        qsettings.setValue(key, value)

    def getSettingsVariable(self, key):
        qsettings = QtCore.QSettings()
        return qsettings.value(key)

    def addMenuBar(self, name):
        menu = QMenu(iface.mainWindow())
        menu.setObjectName(name)
        menu.setTitle(name)
        iface.mainWindow().menuBar().insertMenu(iface.firstRightStandardMenu().menuAction(), menu)
        return menu

    def getShortcutKey(self, shortcutKeyName):
        keys = {
            'Y': QtCore.Qt.Key_Y,
            'B': QtCore.Qt.Key_B,
        }
        if not shortcutKeyName in keys:
            return
        return keys[shortcutKeyName]

    def createAction(self, name, iconPath, callback, shortcutKeyName, checkable):
        a = QAction(
            QIcon(iconPath),
            name,
            iface.mainWindow()
        )
        if self.getShortcutKey(shortcutKeyName):
            a.setShortcut(self.getShortcutKey(shortcutKeyName))
        a.setCheckable(checkable)
        a.triggered.connect(callback)
        return a

    def getVersion(self):
        return core.QgsExpressionContextUtils.globalScope().variable('qgis_version').split('-')[0]

    def getPluginsVersions(self):
        pluginsVersions = []
        for name, plugin in plugins.items():
            try:
                metadata_path = os.path.join(
                    plugin.plugin_dir,
                    'metadata.txt'
                )
                with open(metadata_path) as mf:
                    cp = ConfigParser()
                    cp.readfp(mf)
                    pluginsVersions.append(
                        {
                            'nome' : name,
                            'versao' : cp.get('general', 'version').split('-')[0]
                        }
                    )
            except AttributeError:
                pass
        return pluginsVersions

    def addDockWidget(self, dockWidget):
        iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget)
    
    def removeDockWidget(self, dockWidget):
        if not dockWidget.isVisible():
            return
        iface.removeDockWidget(dockWidget)