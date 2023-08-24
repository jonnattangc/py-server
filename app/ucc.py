try:
    import logging
    import sys
    import os
    import pymysql.cursors
    from datetime import datetime

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class Ucc() :
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

    def isConnect(self) :
        return self.db != None

    def getInfo(self, rut) :
        logging.info("Get information to rut: " + str(rut) )
        data = None
        if self.isConnect() : 
            try :
                if self.db != None :
                    cursor = self.db.cursor()
                    sql = """select * from peopleucc where rut = %s"""
                    cursor.execute(sql, (rut))
                    results = cursor.fetchall()
                    for row in results:
                        date_bd = str(row['birth'])
                        date_send = datetime.strptime(date_bd, '%Y-%m-%d %H:%M:%S')
                        date_birth = date_send.strftime('%Y-%m-%d')
                        data = {
                            'rut'  : str(row['rut']),
                            'name'  : str(row['name']),
                            'adrs'  : str(row['address']),
                            'adrcom'  : str(row['comercial_address']),
                            'mobile'  : str(row['mobile']),
                            'phone'  : str(row['mobile']),
                            'commune'  : str(row['commune']),
                            'mail'  : str(row['mail']),
                            'birth'  : str(date_birth),
                        }
            except Exception as e:
                print("ERROR BD:", e)
        return data
