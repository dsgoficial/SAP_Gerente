import os, sys, psycopg2
import json

class Postgresql(object):

    config_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'config.json'
    )

    def __init__(
            self,
            dbName,
            dbUser,
            dbIP,
            dbPort,
            dbPass
        ):
        super(Postgresql, self).__init__()
        conn = psycopg2.connect(
            u"dbname='{0}' user='{1}' host='{2}' port='{3}' password='{4}'".format(
                dbName,
                dbUser,
                dbIP,
                dbPort,
                dbPass
            )
        )
        conn.set_session(autocommit=True)
        self.cursor = conn.cursor()

    def execute(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
