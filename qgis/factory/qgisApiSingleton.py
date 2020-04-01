from Ferramentas_Gerencia.qgis.factory.qgisApiBuilder import QgisApiBuilder
from Ferramentas_Gerencia.qgis.factory.qgisApiDirector import QgisApiDirector

class QgisApiSingleton:

    qgisApi = None

    @staticmethod
    def getInstance():
        if not QgisApiSingleton.qgisApi:
            apiGisDirector = QgisApiDirector()
            apiQgisBuilder = QgisApiBuilder()
            apiGisDirector.constructQgisApi(apiQgisBuilder)
            QgisApiSingleton.qgisApi = apiQgisBuilder.getResult()
        return QgisApiSingleton.qgisApi