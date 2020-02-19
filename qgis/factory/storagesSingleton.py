from Ferramentas_Gerencia.qgis.storages.storages import Storages

class StoragesSingleton:

    storages = None

    @staticmethod
    def getInstance():
        if not StoragesSingleton.storages:
            StoragesSingleton.storages = Storages()
        return StoragesSingleton.storages