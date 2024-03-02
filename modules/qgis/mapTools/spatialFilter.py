from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore

from SAP_Gerente.modules.qgis.interfaces.IMapTool import IMapTool

class SpatialFilter(IMapTool):

    def __init__(self):
        super(SpatialFilter, self).__init__()
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
        geometryWkt = self.rubberBand.asGeometry().asWkt()=
        epsgid = iface.mapCanvas().mapSettings().destinationCrs().authid().replace("EPSG:", "")
        vectorLayer = core.QgsVectorLayer(
            "?query=SELECT geom_from_wkt('{0}') as geometry&geometry=geometry:3:{1}".format(geometryWkt, epsgid), 
            "Polygon_Reference", 
            "virtual"
        )
        core.QgsProject.instance().addMapLayer(vectorLayer)            
        for layer in iface.mapCanvas().layers():
            try:
                layer.setSubsetString(
                    "st_intersects(geom,st_geomfromewkt('SRID={0};{1}'))".format(epsgid, geometryWkt)
                )
            except Exception:
                pass
        iface.mapCanvas().refresh()
        self.rubberBand.reset(core.QgsWkbTypes.PolygonGeometry)