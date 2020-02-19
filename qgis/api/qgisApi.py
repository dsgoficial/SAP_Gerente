from Ferramentas_Gerencia.qgis.interfaces.IQgisApi import IQgisApi

from qgis import gui, core
from qgis.utils import plugins, iface
from configparser import ConfigParser
import os

class QgisApi(IQgisApi):

    def __init__(self):
        self.storages = None
        self.layers = None
        self.styles = None

    def setLayers(self, layers):
        self.layers = layers

    def getLayers(self):
        return self.layers
    
    def setStyles(self, styles):
        self.styles = styles

    def getStyles(self):
        return self.styles
    
    def setStorages(self, storages):
        self.storages = storages

    def getStorages(self):
        return self.storages

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