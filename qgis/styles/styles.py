from qgis import gui, core
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import plugins, iface

import os
import uuid

from Ferramentas_Gerencia.qgis.interfaces.IStyles import IStyles

class Styles(IStyles):
    
    tmpFolderPath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'tmp'
    )

    def __init__(self):
        super(Styles, self).__init__()

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
        