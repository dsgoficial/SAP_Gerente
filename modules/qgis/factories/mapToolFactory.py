from Ferramentas_Gerencia.modules.qgis.mapTools.removeByClip  import RemoveByClip
from Ferramentas_Gerencia.modules.qgis.mapTools.removeByIntersect  import RemoveByIntersect

class MapToolFactory:

    def getMapTool(self, toolName):
        mapTools = {
            'removeByClip': RemoveByClip,
            'removeByIntersect': RemoveByIntersect
        }
        return mapTools[toolName]()
       