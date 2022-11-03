from qgis.utils import iface
from qgis import gui, core

class MapFunction:

    def __init__(self):
        super(MapFunction, self).__init__()        
        
    def getShortestDistanceBetweenGeometries(self, sourceFeature, targetFeature):
        return sourceFeature.distance(targetFeature.nearestPoint(sourceFeature))

    def getPointsIndexOfTheNearestSegment(self, sourceFeature, targetFeature):
        sourceGeometry = sourceFeature.geometry()
        targetGeometry = targetFeature.geometry()
        firstVertexIdx = 0
        lastVertexIdx = len(sourceGeometry.asPolyline())-1
        firstVertex = sourceGeometry.vertexAt(0)
        lastVertex = sourceGeometry.vertexAt(lastVertexIdx)
        distance1 = self.getShortestDistanceBetweenGeometries(
            core.QgsGeometry.fromPointXY(core.QgsPointXY(firstVertex.x(), firstVertex.y())), 
            targetGeometry
        )
        distance2 = self.getShortestDistanceBetweenGeometries(
            core.QgsGeometry.fromPointXY(core.QgsPointXY(lastVertex.x(), lastVertex.y())), 
            targetGeometry
        )
        vertexIdx = -1
        if distance1 < distance2:
            vertexIdx = firstVertexIdx
        else:
            vertexIdx = lastVertexIdx
        adjVetexIdx1, adjVetexIdx2 = sourceGeometry.adjacentVertices(vertexIdx)
        adjVetexIdx = adjVetexIdx1 if (adjVetexIdx1 != -1) else adjVetexIdx2
        return (adjVetexIdx, vertexIdx)

    def getFeatureById(self, layer, featureId):
        f = core.QgsFeature()
        it = layer.getFeatures(core.QgsFeatureRequest(featureId))
        it.nextFeature(f)
        return f

    def intersectingGeometries(self, sourceGeometry, targetGeometry):
        return sourceGeometry.intersects(targetGeometry)

    def run(self, *args):
        pass