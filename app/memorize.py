#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import pymysql.cursors
    from datetime import datetime, timedelta
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[Memorize] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class Memorize() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
    database = 'gral-purpose'

    def __init__(self) :
        try:
            self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def __del__(self):
        if self.db != None:
            self.db.close()

    def connect( self ) :
        try:
            if self.db == None :
                self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def isConnect(self) :
        return self.db != None
    # ==============================================================================
    def get_states(self) :
        names = []
        states = []
        try :
            if self.isConnect() :
                cursor = self.db.cursor()
                sql = """select * from game_states where client = %s"""
                cursor.execute(sql, ('ionix-day'))
                results = cursor.fetchall()
                for row in results:
                    state = str(row['state'])
                    name = str(row['name_state'])
                    states.append(state)
                    names.append(name)
                    # logging.info("Rescato card: " + name + " estado: " + state )
        except Exception as e:
            print("ERROR BD:", e)
        
        return names, states
# ==============================================================================
    def reset(self ) :
        msg = 'Ha ocurrio un error'
        code = 500
        try :
            if self.isConnect() :
                cursor = self.db.cursor()
                sql = """UPDATE game_states set state=%s where client=%s"""
                cursor.execute(sql, ('down', 'ionix-day'))
                self.db.commit()
                msg = 'Servicio Ejecutado exitosamente'
                code = 200
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
        return msg, code
# ==============================================================================
    def save_process(self, card, state) :
        visible = False
        if str(state) == 'down' :
            visible = False
        else : 
            visible = True
        code = 500
        try :
            if self.isConnect() :
                cursor = self.db.cursor()
                sql = """UPDATE game_states set state=%s where client=%s and name_state=%s"""
                cursor.execute(sql, (state, 'ionix-day', card ))
                self.db.commit()
                code = 200
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
            visible = not visible
        return visible, code
# ==============================================================================
    def process(self, json_data ) :
        return self.save_process( str(json_data['card']), str(json_data['state']))
