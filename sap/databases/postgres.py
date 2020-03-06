import psycopg2

class Postgres:
    
    def __init__(self):
        self.connection = None
        
    def setConnection(self, dbName, dbHost, dbPort, dbUser, dbPassword):
        self.connection = psycopg2.connect(
            u"dbname='{0}' user='{1}' host='{2}' port='{3}' password='{4}'".format(
                dbName, dbUser, dbHost, dbPort, dbPassword
            )
        )
        self.connection.set_session(autocommit=True)

    def getConnection(self):
        return self.connection

    def getLayers(self):
        pgCursor = self.getConnection().cursor()
        pgCursor.execute('''
        SELECT f_table_name, f_table_schema FROM geometry_columns;
        ''')
        query = pgCursor.fetchall()
        pgCursor.close()
        return [ 
            {
                'nome': row[0],
                'schema': row[1]
            } for row in query
        ]
