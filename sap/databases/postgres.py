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

    def insertStyle(self, 
            f_table_schema, 
            f_table_name, 
            f_geometry_column, 
            stylename, 
            styleqml, 
            stylesld,
            owner, 
            ui, 
            update_time
        ):
        pgCursor = self.getConnection().cursor()
        pgCursor.execute('''
        INSERT INTO layer_styles(f_table_schema, f_table_name, f_geometry_column, stylename, styleqml, stylesld, owner, ui, update_time)
             VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);
        ''', (f_table_schema, f_table_name, f_geometry_column, stylename, styleqml, stylesld, owner, ui, update_time,))
        pgCursor.close()

    def insertStyles(self, styles):
        for style in styles:
            self.insertStyle(
                style['f_table_schema'],
                style['f_table_name'], 
                style['f_geometry_column'], 
                style['stylename'], 
                style['styleqml'], 
                style['stylesld'], 
                style['owner'], 
                style['ui'], 
                style['update_time']
            )

    def insertModel(self, nome, descricao, model_xml, owner, update_time):
        pgCursor = self.getConnection().cursor()
        pgCursor.execute('''
        INSERT INTO layer_qgis_models(nome, descricao, model_xml, owner, update_time)
             VALUES(%s, %s, %s, %s, %s);
        ''', (nome, descricao, model_xml, owner, update_time,))
        pgCursor.close()

    def insertModels(self, models):
        for model in models:
            self.insertModel(
                model['nome'],
                model['descricao'],
                model['model_xml'],
                model['owner'],
                model['update_time']
            )

    def insertRule(self, grupo_regra_id, schema, camada, atributo, regra, descricao, owner, update_time):
        pgCursor = self.getConnection().cursor()
        pgCursor.execute('''
        INSERT INTO layer_rules(grupo_regra_id, schema, camada, atributo, regra, descricao, owner, update_time)
             VALUES(%s, %s, %s, %s, %s, %s, %s, %s);
        ''', (1, schema, camada, atributo, regra, descricao, owner, update_time,))
        pgCursor.close()

    def insertRules(self, rules):
        for rule in rules:
            self.insertRule(
                rule['grupo_regra_id'],
                rule['schema'],
                rule['camada'],
                rule['atributo'],
                rule['regra'],
                rule['descricao'],
                rule['owner'],
                rule['update_time']
            )

    def insertMenu(self, nome, definicao_menu, owner, update_time):
        pgCursor = self.getConnection().cursor()
        pgCursor.execute('''
        INSERT INTO layer_menus(nome, definicao_menu, owner, update_time)
             VALUES(%s, %s, %s, %s);
        ''', (nome, definicao_menu, owner, update_time,))
        pgCursor.close()

    def insertMenus(self, menus):
        for menu in menus:
            self.insertMenu(
                menu['nome'],
                menu['definicao_menu'],
                menu['owner'],
                menu['update_time']
            )