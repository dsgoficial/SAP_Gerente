from Ferramentas_Gerencia.qgis.mapTools.removeByClip  import RemoveByClip
from Ferramentas_Gerencia.qgis.mapTools.removeByIntersect  import RemoveByIntersect

class MapToolsFactoryMethod:

    @staticmethod
    def getMapTool(toolName):
        if toolName == 'removeByClip':
            return RemoveByClip()
        elif toolName == 'removeByIntersect':
            return RemoveByIntersect()
       