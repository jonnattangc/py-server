try:
    import logging
    import sys
    import os
    import time
    import hashlib
    import json
    import requests
    import pymysql.cursors
    from datetime import datetime, timedelta
    from flask import jsonify
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[Irelez] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class Irelez() :
    db = None

    def __init__(self) :
        try:
            host = str(os.environ.get('HOST_BD','dev.jonnattan.com'))
            port = int(os.environ.get('PORT_BD', 3306))
            user_bd = str(os.environ.get('USER_BD','----'))
            pass_bd = str(os.environ.get('PASS_BD','*****'))
            eschema = str(os.environ.get('SCHEMA_BD','*****'))
            self.db = pymysql.connect(host=host, port=port, 
                user=user_bd, password=pass_bd, database=eschema, 
                cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR __init__:", e)
            self.db = None

    def __del__(self):
        if self.db != None:
            self.db.close()

    def is_connect(self) :
        return self.db != None

    def get_config(self) :
        config = {}
        try :
            if self.is_connect() :
                cursor = self.db.cursor()
                sql = """select p.environment, p.request, p.response, p.enabled, p.hash, p.id as id, k.coverage_key, k.ot_key, k.geo_key, k.base_url from `gral-purpose`.proxy p inner join `gral-purpose`.keys k on p.id = k.proxy_id and p.environment = k.environment where p.client = 'zeleri'"""
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    config = {
                        'environment': str(row['environment']),
                        'request' : str(row['request']),
                        'response' : str(row['response']),
                        'enabled' : bool(row['enabled']),
                        'hash' : str(row['hash']),
                        'id' : int(row['id']),
                        'cov': str(row['coverage_key']),
                        'ot' : str(row['ot_key']),
                        'geo' : str(row['geo_key']),
                        'url' : str(row['base_url'])
                    }
                    break
        except Exception as e:
            print("ERROR BD:", e)
            config = {}
        logging.info("Configuracion para ambiente de [" + str(config) + "]" )
        return config

    def saveEnv(self, env) :
        success = False
        current = self.getEnv()
        try :
            if self.is_connect() and self.environment != env:
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

    def saveCache(self, request: str, hash: str, response: str, id: int ) :
        success = False
        try :
            if self.is_connect() :
                cursor = self.db.cursor()
                sql = """UPDATE proxy set request=%s, response=%s, hash=%s where id=%s"""
                cursor.execute(sql, (request, response, hash, id))
                self.db.commit()
                success = True
                logging.info('Cache actualizado con exito')
        except Exception as e:
            print("ERROR BD saveCache():", e)
            self.db.rollback()

    def get_key_by_path(self, congig: dict, path: str) :
        key = ''
        if path.find('rating/') >= 0 or path.find('Rating/') >= 0 :
            key = congig['cov']
        if path.find('transport-orders/') >= 0  :
            key = congig['ot']
        if path.find('georeference/') >= 0  :
            key = congig['geo']
        if path.find('checkout/orders') >= 0  :
            key = congig['geo']
        return key

    def request_process(self, request, subpath ) :
            logging.info("========================================== /ZLR =============================================================" )
            logging.info("Reciv " + str(request.method) + " Contex: /" + str(subpath) )
            logging.info("Reciv Header : " + str(request.headers) )
            logging.info("Reciv Data: " + str(request.data) )
            
            authorization = request.headers.get('Authorization')
            logging.info("-----> Authorization Rx: " + str(authorization) )

            config = self.get_config()
            jwt_token = self.get_key_by_path(config, subpath)

            url = config['url'] + str(subpath).replace('integration','').replace('production','')
            logging.info("URL: " + str(url) )

            if jwt_token != None and jwt_token != '' :
                authorization = "Bearer " + str(jwt_token)
            
            logging.info("-----> Authorization Tx: " + str(authorization) )
            
            headers = {
                'Authorization': str(authorization), 
                'Content-Type': 'application/json' 
            }

            # valores por defecto
            data_response = jsonify({'statusCode': 500, 'statusDescription': 'Error interno Gw' })
            errorCode = 500
            m1 = time.monotonic()
            diff = 0
            try :
                resp = None
                if (request.method == 'POST' ) :
                    logging.info("POST URL : " + url )
                    resp = requests.post(url, data = request.data, headers = headers, timeout = 120)
                    diff = time.monotonic() - m1;
                if (request.method == 'PUT' ) :
                    logging.info("PUT URL : " + url )
                    resp = requests.put( url, data = request.data, headers = headers, timeout = 120)
                    diff = time.monotonic() - m1;
                if (request.method == 'GET' ) :
                    logging.info("GET URL : " + url )
                    resp = requests.get(url, data = request.data, headers = headers, timeout = 120)
                    diff = time.monotonic() - m1;
                errorCode = resp.status_code
                if resp.status_code == 200 :
                    data_response = resp.json()
                    logging.info("Response OK: " + str(data_response) )
                else :
                    data_response = resp.json()
                    logging.info("Response NOK[" + str(resp.status_code) + "]: " + str( data_response ) )
            except Exception as e:
                print("ERROR POST:", e)
                diff = time.monotonic() - m1;
            logging.info("Time Response in " + str(diff) + " sec." )
            return data_response, errorCode
