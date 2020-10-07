from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore

from Ferramentas_Gerencia.modules.qgis.interfaces.IMapTool import IMapTool

class RemoveByIntersect(IMapTool):

    def __init__(self):
        super(RemoveByIntersect, self).__init__()
        self.isEditing = False
        self.tool = None

    def start(self):
        self.tool = gui.QgsMapToolEmitPoint(iface.mapCanvas())
        self.tool.canvasClicked.connect(self.mouseClick)
        self.rubberBand = gui.QgsRubberBand(
            iface.mapCanvas(),
            core.QgsWkbTypes.PolygonGeometry
        )
        color = QtGui.QColor(78, 97, 114)
        color.setAlpha(190)
        self.rubberBand.setColor(color)
        self.rubberBand.setFillColor(QtGui.QColor(255, 0, 0, 40))
        iface.mapCanvas().setMapTool(self.tool)
        iface.mapCanvas().xyCoordinates.connect(self.mouseMove)

    def mouseMove(self, currentPos):
        if not self.isEditing:
            return
        self.rubberBand.movePoint(core.QgsPointXY(currentPos))

    def mouseClick(self, currentPos, clickedButton):
        if clickedButton == QtCore.Qt.LeftButton:
            self.rubberBand.addPoint(core.QgsPointXY(currentPos))
            self.isEditing = True
            return
        if not ( clickedButton == QtCore.Qt.RightButton and self.rubberBand.numberOfVertices() > 2 ):
            return
        self.isEditing = False
        geomRubber = self.rubberBand.asGeometry()
        node_layers = core.QgsProject.instance().layerTreeRoot().findLayers()
        if not self.checkValidity(geomRubber):
            iface.mapCanvas().refresh()
            self.rubberBand.reset(core.QgsWkbTypes.PolygonGeometry)
            return
        layers = [x.layer() for x in node_layers if x.isVisible()]
        for layer in layers:
            new_geom = []
            layer.startEditing()
            features = layer.getFeatures()
            for feat in features:
                geom = feat.geometry()                       
                if not geom.intersects(geomRubber):
                    continue
                layer.deleteFeature(feat.id())
        iface.mapCanvas().refresh()
        self.rubberBand.reset(core.QgsWkbTypes.PolygonGeometry)

    def checkValidity(self, geomRubber):
        if geomRubber.isGeosValid():
            return True
        iface.messageBar().pushMessage(
            "Erro", "Geometria inválida", level=core.Qgis.Critical)
        self.rubberBand.reset(core.QgsWkbTypes.PolygonGeometry)
        return False