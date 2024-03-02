from SAP_Gerente.modules.qgis.mapTools.removeByClip  import RemoveByClip
from SAP_Gerente.modules.qgis.mapTools.removeByIntersect  import RemoveByIntersect

class MapToolFactory:

    def getMapTool(self, toolName):
        mapTools = {
            'removeByClip': RemoveByClip,
            'removeByIntersect': RemoveByIntersect
        }
        return mapTools[toolName]()
       