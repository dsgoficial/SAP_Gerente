from Ferramentas_Gerencia.sap.databases.postgres  import Postgres

class DatabasesFactoryMethod:

    @staticmethod
    def getDatabase(database):
        if database == 'postgres':
            return Postgres()
       