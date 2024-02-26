try:
    import logging
    import sys
    import os
    import json
    import pymysql.cursors
    from datetime import datetime
    from jose import jwe
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[Deposits] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

ROOT_DIR = os.path.dirname(__file__)

class Deposits() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
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

    def __init__(self, root=ROOT_DIR, filename='bank/banks') :
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

    def getBank(self, idBank) :
        name = None
        account = None
        for bank in self.banks :
            if bank.id == int(idBank) :
                name = bank.name
                account = bank.account
                break
        return name, account

class Bank() :
    name = ''
    account = ''
    id = -1

    def __init__(self, id, account, name) :
        self.id = id
        self.account = account
        self.name = name

    def __del__(self):
        self.name = ''
        self.account = ''
        self.id = -1

class Cipher() :
    aes_key = ''
    algorithm = ''

    def __init__(self, algorithm='aes') :
        self.id = id
        self.aes_key = 'dRgUkXp2s5v8y/B?E(H+MbQeThVmYq3t' # 256 bit
        self.algorithm = algorithm

    def __del__(self):
        self.aes_key = ''
        self.algorithm = ''

    def aes_encrypt(self, payload ) :
        data_cipher = None
        try :
            logging.info("Cifro " + str(self.algorithm))
            data_cipher = jwe.encrypt(payload, key=self.aes_key, algorithm='dir', encryption='A256GCM')
        except Exception as e:
            print("ERROR Cipher:", e)
            data_cipher = None
        return data_cipher

    def aes_decrypt(self, data ) :
        data_clear = None
        try :
            logging.info("Decifro " + str(self.algorithm))
            data_clear = jwe.decrypt(data, key=self.aes_key )
        except Exception as e:
            print("ERROR Decipher:", e)
            data_clear = None
        return data_clear