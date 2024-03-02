from SAP_Gerente.modules.databases.postgres  import Postgres

class DatabasesFactory:

    def getDatabase(self, databaseName):
        databaseNames = {
            'Postgresql' : Postgres
        }
        return databaseNames[databaseName]()
       