#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import requests
    import pymysql.cursors
    from datetime import datetime, timedelta
    from flask_httpauth import HTTPBasicAuth
    from flask import Flask, render_template, abort, make_response, request, redirect, jsonify, send_from_directory
    from utils import Banks, Deposits
except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:',
                                 str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

############################# Configuraci'on de Coordinador ################################

class Coordinator() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
    database = 'deposits'
    # URL notificacion a middleware IONIX
    url_notification = str(os.environ.get('NOTIFICATION_URL','None')) + '/' + database

    transbot_id = -1

    def __init__(self) :
        try:
            self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
            self.transbot_id = int(os.environ.get('TRANSBOT_ID','-1'))
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def __del__(self):
        if self.db != None:
            self.db.close()

    # Evalua la fecha de 
    def getEvaluateDates(self, id_bank ) :
        banks = Banks()
        name, account = banks.getBank( id_bank )
        del banks
        
        now = datetime.now()
        yesterday = now - timedelta(1) 
        initial_date = yesterday.strftime("%d/%m/%Y")

        if( name != None and account != None ) :
            cursor = self.db.cursor()
            try:
                sql = """SELECT d.date_information as date FROM deposits.deposit d WHERE d.destination_account = %s ORDER BY d.date_information DESC limit 1"""
                cursor.execute(sql, (str(account)))
                results = cursor.fetchall()
                for row in results:
                    date_bd = str(row['date'])
                    from_date = datetime.strptime(date_bd, '%Y-%m-%d %H:%M:%S')
                    initial_date = from_date.strftime("%d/%m/%Y")
            except Exception as e:
                    print("ERROR BD:", e)

        logging.info(str(name) + '[' + str(id_bank) + ']: ' + str(account) )
        
        data = {
            "status": "success",
            "deposits": {
                "from_date" : initial_date,
                "to_date"   : now.strftime("%d/%m/%Y")
            },
        }
        return data

    def notifyMiddleware( self, deposit, account, id_bank ) : 
        request_tx = {
            'data': {
                'transbotID'    : self.transbot_id,
                'amount'        : int(deposit.amount),
                'name'          : deposit.origin_name.upper(),
                'identity'      : deposit.identity,
                'bank'          : deposit.origin_bank.upper(),
                'account'       : deposit.origin_account.upper(),
                'date'          : deposit.date_registry.upper(),
                'bank_account'  : account, # cuenta banco destino del deposito
            },
            'bank': id_bank
        }
        logging.info("Request to IONIX Middleware: " + str(request_tx) )
        response = {}
        try :
            headersTx = {'Content-Type': 'application/json','Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJhQGEuY2wiLCJpYXQiOjE2Njc5MTQ2MjAsImV4cCI6MTcwODA5MDYyMH0.Y7eperR1KbJDHdyIKqaw9djzG6MPYadBq3pAxnuUUeo' }
            response = requests.post(self.url_notification, json = request_tx, headers = headersTx, timeout = 20)
        except Exception as e:
            print("ERROR POST:", e)
        if response.status_code != None and response.status_code == 200 :
            data_response = response.json()
            logging.info("Response : " + str( data_response ) )

    # Procesa dato que llega desde Bot
    def processUpdate(self, deposit_bank_name, deposit_bank_account, deposit_bank_internal_id, deposits ) :
        logging.info('Cuenta [' + deposit_bank_internal_id + '] del ' + deposit_bank_name + ' N°: ' + deposit_bank_account )
        status = 'success'
        for deposit in deposits :
            logging.info('Deposito ' + str(deposit) )
            cursor = self.db.cursor()
            data = Deposit( deposit )
            try:
                sql = """select count(*) as count from deposit where identity = %s"""
                cursor.execute(sql, (deposit['identity']))
                results = cursor.fetchall()
                count = 0
                for row in results:
                    count = int(str(row['count']))

                if count == 0 :
                    sql = """INSERT INTO deposit (amount, origin_name, transbot_id, origin_bank, destination_bank, origin_account, destination_account, 
                        date_information, create_at, update_at, `identity`, internal_bot_process, channel, origin_rut, 
                                                destination_rut, description, balance, comment, type )
                                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    now = datetime.now()
                    cursor.execute(sql, (data.amount, data.origin_name, self.transbot_id, data.origin_bank,deposit_bank_name, data.origin_account, deposit_bank_account, 
                        data.date_registry, now.strftime("%Y/%m/%d %H:%M:%S"), now.strftime("%Y/%m/%d %H:%M:%S"), data.identity, data.internal_bot_process, data.channel, data.origin_rut,
                        data.destination_rut, data.description, data.balance, data.comment, data.type_mov ) )
                    self.db.commit()
                    self.notifyMiddleware( data, deposit_bank_account, deposit_bank_internal_id )
                else :
                    print("Existen: " + str(count) + " tuplas con el id: " + data.identity )
                
                del data
            except Exception as e:
                print("ERROR BD:", e)
                status = 'error'
                self.db.rollback()

        return  {
                    "status": str(status)
                }

    def proccessSolicitude( self, req , paths ) :
        dataTx = {}
        if len(paths) >= 3 :
            logging.info('paths[2]: ' + str(paths[2]) )
            if paths[2].find('bank_dates') >= 0 :
                id = req.args.get('id', '-1')
                dataTx =  self.getEvaluateDates( id )
            elif paths[2].find('bank_deposits_update') >= 0 :
                request_data = req.get_json()
                id_bank = str(request_data['platform_bank_id'])
                banks = Banks()
                name, account = banks.getBank( id_bank )
                del banks
                if name != None and account != None :
                    dataTx = self.processUpdate( str(name), str(account), id_bank, request_data['deposits'] )
                else: 
                    dataTx =  {
                        "status": "error"
                     }
            elif paths[2].find('ping') >= 0 :
                dataTx =  {}
            else : # otras notificaciones
                dataTx =  {
                    "status": "success"
                }
        return dataTx

class Deposit() :

    origin_bank = None 
    origin_account = None 
    date_registry = None 
    amount = None 
    origin_name = None 
    identity = None 
    internal_bot_process = None 
    channel = None 
    origin_rut = None 
    destination_rut = None 
    description = None 
    balance = None 
    comment = None 
    type_mov = None 


    def __init__(self, deposit ) :
        self.process( deposit )

    def __del__(self):
        self.origin_bank = None 
        self.origin_account = None 
        self.date_registry = None 
        self.amount = None 
        self.origin_name = None 
        self.identity = None 
        self.internal_bot_process = None 
        self.channel = None 
        self.origin_rut = None 
        self.destination_rut = None 
        self.description = None 
        self.balance = None 
        self.comment = None 
        self.type_mov = None 

    def process(self, deposit ) :
        try : 
            self.origin_bank = deposit['origin_bank']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)
        
        try : 
            self.origin_account = deposit['origin_account']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.date_registry = deposit['date']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.amount = deposit['amount']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.origin_name = deposit['origin_name']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.identity = deposit['identity']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.internal_bot_process = deposit['internal_bot_process']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.channel = deposit['channel']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.origin_rut = deposit['origin_rut']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.destination_rut = deposit['destination_rut']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.description = deposit['description']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.balance = deposit['balance']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)

        try : 
            self.comment = deposit['comment']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)
        
        try : 
            self.type_mov = deposit['type']
        except Exception as e:
            print("ERROR, No se encuentra: ", e)
