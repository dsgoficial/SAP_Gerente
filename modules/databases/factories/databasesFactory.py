from Ferramentas_Gerencia.modules.databases.postgres  import Postgres

class DatabasesFactory:

    def getDatabase(self, databaseName):
        databaseNames = {
            'Postgresql' : Postgres
        }
        return databaseNames[databaseName]()
       