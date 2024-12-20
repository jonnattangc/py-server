try:
    import logging
    import sys
    import os
    import time
    import requests
    import pymysql.cursors
    from datetime import datetime, timedelta
    from flask import jsonify
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[Sserpxelihc] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class Sserpxelihc() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
    database = 'proxy'
    environment = None

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

    def getEnv(self) :
        name = None
        try :
            if self.isConnect() :
                cursor = self.db.cursor()
                sql = """select * from proxy where client = %s"""
                cursor.execute(sql, ('chilexpress'))
                results = cursor.fetchall()
                for row in results:
                    self.environment = str(row['environment'])
                    name = str(row['name'])
        except Exception as e:
            print("ERROR BD:", e)
        logging.info("Rescato ambiente de " + name + ": " + self.environment )
        return self.environment

    def saveEnv(self, env) :
        success = False
        current = self.getEnv()
        try :
            if self.isConnect() and self.environment != env:
                cursor = self.db.cursor()
                sql = """UPDATE proxy set environment=%s where client=%s"""
                cursor.execute(sql, (env,'chilexpress'))
                self.db.commit()
                success = True
                if self.environment != None :
                    self.environment = env
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
        if success :
            logging.info("Actually env is: " + current + " change to: " + str(self.environment))
        else :
            logging.info('Error cambiando ambiente, puede ser que sea el mismo que ya existia')
        return current, success

    def requestProcess(self, request, subpath ) :
            logging.info("Reciv " + str(request.method) + " Contex: " + str(subpath) )
            logging.info("Reciv Header : " + str(request.headers) )
            logging.info("Reciv Data: " + str(request.data) )
            currentEnv = self.getEnv()

            url = 'https://devservices.wschilexpress.com/' + str(subpath)
            key = 'cfa9de51f151482b98477655dc346443'

            if( currentEnv.find('test') >= 0 ) :
                url = 'https://testservices.wschilexpress.com/' + str(subpath)
                if( subpath.find('rating/') >= 0 or subpath.find('Rating/') >= 0 ) :
                    key = 'fd46aa18a9fe44c6b49626692605a2e8'
                if( subpath.find('transport-orders/') >= 0 ) :
                    key = '0112f48125034f8fa42aef2441773793'

            if( currentEnv.find('qa') >= 0 ) :
                url = 'https://qaservices.wschilexpress.com/' + str(subpath)
                if( subpath.find('rating/') >= 0 or subpath.find('Rating/') >= 0 ) :
                    key = 'f25fbe75153b4f8e908e11fb5c958a1d'
                    #key = 'fd46aa18a9fe44c6b49626692605a2e8'
                if( subpath.find('transport-orders/') >= 0  ) :
                    key = '5a77a19b76a24297ba01c158286641b7'
                if( subpath.find('georeference/') >= 0  ) :
                    key = 'a6979b4160c6465f85776f43b6c40ffb'
                    #key = '134b01b545bc4fb29a994cddedca9379'

            headers = {'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/json' }
            # valores por defecto
            data_response = jsonify({'statusCode': 500, 'statusDescription': 'Error interno Gw' })
            errorCode = 500
            try :
                m1 = time.monotonic()
                resp = None
                if (request.method == 'POST' ) :
                    logging.info("URL : " + url )
                    resp = requests.post(url, data = request.data, headers = headers, timeout = 40)
                    diff = time.monotonic() - m1;

                if (request.method == 'PUT' ) :
                    logging.info("URL : " + url )
                    resp = requests.put( url, data = request.data, headers = headers, timeout = 40)
                    diff = time.monotonic() - m1;

                if (request.method == 'GET' ) :
                    if ( subpath.find('agendadigital/') >= 0  ) :
                        key = '9c853753ce314c81934c4f966dad7755'
                        url = 'https://services.wschilexpress.com/' + str(subpath)
                        headers = {'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/json' }
                        fecha = request.args.get('fecha', '-1')
                        if ( fecha != '-1' and subpath.find('GetArticulos') < 0 ) :
                            url = url + "?fecha=" + fecha
                    else:
                        region = request.args.get('RegionCode', '-1')
                        tipo = request.args.get('type', '-1')
                        if ( region != '-1' and tipo != '-1' ) :
                            url = url + "?RegionCode=" + region + "&type=" + tipo
                    # se reevia la peticion
                    logging.info("URL : " + url )
                    resp = requests.get(url, data = request.data, headers = headers, timeout = 40)
                    diff = time.monotonic() - m1;
                errorCode = resp.status_code

                logging.info("================================================" )
                logging.info("Environment : " + str(currentEnv) )
                logging.info("Key : " + key )
                
                if( resp.status_code == 200 ) :
                    data_response = resp.json()
                    logging.info("Response CXP OK" + str( data_response ) )
                else :
                    data_response = resp.json()
                    logging.info("Response CXP NOK" + str( data_response ) )

                logging.info("Time Response in " + str(diff) + " sec." )

            except Exception as e:
                print("ERROR POST:", e)

            return data_response, errorCode
