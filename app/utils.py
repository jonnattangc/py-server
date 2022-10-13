try:
    import logging
    import sys
    import os
    import time
    import json
    import pymysql.cursors
    from datetime import datetime, timedelta
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class Deposits() :
    db = None
    host = '192.168.0.15'
    user = 'python-dev'
    password = 'PythonDev'
    database = 'deposits'
    transbot_id = '1'

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

    def save( self, amount, name, identity, origin_bank, origin_account, date, destination_bank, destination_account ) :
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """INSERT INTO deposit (amount, name, transbot_id, origin_bank, destination_bank, origin_account,
                    destination_account, date_information, create_at, update_at, `identity`)
                      VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                now = datetime.now()
                cursor.execute(sql, (amount, name, self.transbot_id, origin_bank, destination_bank,
                    origin_account, destination_account, date,
                        now.strftime("%Y/%m/%d %H:%M:%S"), now.strftime("%Y/%m/%d %H:%M:%S"), identity ))
                self.db.commit()
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()



class Banks():
    banks = []
    json_banks = {}

    def __init__(self, root='./', filename='') :
        try:
            file_path = os.path.join(root, 'static/' + str(filename) + '.json')
            with open(file_path) as file:
                self.json_banks = json.load(file)
                file.close()
            for bank in self.json_banks['data'] :
                self.banks.append( self.process(bank) )
        except Exception as e :
            print("ERROR File:", e)
            self.banks = []
            self.json_banks = {}

    def __del__(self):
        self.banks = None
        self.json_banks = None

    def process( self, bank ) :
        name = bank['account']['bank']
        name = str(name['name'])
        account = str(bank['account']['number'])
        id = int(bank['id'])
        return Bank( id, account, name )

    def getBank(self, id) :
        name = None
        account = None
        for bank in self.json_banks :
            if bank.id == int(id) :
                name = bank.name
                account = bank.account
                break
        return name, account

class Bank() :
    name = None
    account = None
    id = -1

    def __init__(self, id, account, name) :
        self.id = id
        self.account = account
        self.name = name

    def __del__(self):
        self.name = None
        self.account = None
        self.id = -1
