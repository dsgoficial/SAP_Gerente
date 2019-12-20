from Ferramentas_Gerencia.qgis.models.storages.storagesQgis import StoragesQgis

class StoragesQgisSingleton:

    storagesQgis = None

    @staticmethod
    def getInstance():
        if not StoragesQgisSingleton.storagesQgis:
            StoragesQgisSingleton.storagesQgis = StoragesQgis()
        return StoragesQgisSingleton.storagesQgis