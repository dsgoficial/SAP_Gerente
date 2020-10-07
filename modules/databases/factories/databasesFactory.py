from Ferramentas_Gerencia.modules.databases.postgres  import Postgres

class DatabasesFactory:

    def getDatabase(databaseName):
        databaseNames = {
            'Postgresql' : Postgres
        }
        return databaseNames[databaseName]()
       