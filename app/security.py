try:
    import logging
    import sys
    import os
    import time
    import json
    import pymysql.cursors
    from datetime import datetime
    from werkzeug.security import generate_password_hash, check_password_hash

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class Security() :
    db = None
    host = '192.168.0.15'
    user = 'jonnattan'
    password = 'wsxzaq123'
    database = 'security'

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

    def verifiyUserPass( self, username, password ) :
        logging.info("Rescato password para usuario: " + str(username) )
        passwordBd = None
        userBd = None
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from basic where username = %s"""
                cursor.execute(sql, (username))
                results = cursor.fetchall()
                for row in results:
                    passwordBd = str(row['password'])
                    userBd = str(row['username'])
                if userBd != None and passwordBd != None :
                    if userBd != username or check_password_hash(password, passwordBd) :
                      userBd = None

        except Exception as e:
            print("ERROR BD:", e)
        return userBd

    def generateUser(self, user, password) :
        logging.info("Genero nuevo usuario: " + str(username) )
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """INSERT INTO basic (create_at, username, password ) VALUES(%s, %s, %s)"""
                now = datetime.now()
                cursor.execute(sql, (now.strftime("%Y-%m-%d %H:%M:%S"), user, generate_password_hash(password)))
                self.db.commit()
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
