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
    print((os.linesep * 2).join(['[Sserpxelihc] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class Sserpxelihc() :
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

    def get_config(self) :
        config = {}
        try :
            if self.isConnect() :
                cursor = self.db.cursor()
                sql = """select p.environment, p.request, p.response, p.enabled, p.hash, p.id as id, k.coverage_key, k.ot_key, k.geo_key, k.base_url, k.meta_data from `gral-purpose`.proxy p inner join `gral-purpose`.keys k on p.environment = k.environment where p.client = 'chilexpress'"""
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results :
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
                        'url' : str(row['base_url']),
                        'meta_data' : row['meta_data']
                    }
                    break
        except Exception as e:
            print("ERROR BD get_config():", e)
            config = {}
        logging.info("Configuracion para ambiente de [" + str(config['environment']) + "]" )
        return config

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

    def saveCache(self, request: str, hash: str, response: str, id: int ) :
        success = False
        try :
            if self.isConnect() :
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
        return key

    def procces_meta_data( self, meta_data: dict, request: dict ) :
        if meta_data is None:
            return request
        if isinstance(meta_data, str):
            try:
                json_meta_data = json.loads(meta_data)
            except json.JSONDecodeError:
                logging.error("meta_data no es un JSON válido")
                return request
        else:
            json_meta_data = meta_data
        json_data = request.copy()
        #logging.info(f"######## Request Entrada: {json_data}")
        for key, value in json_meta_data.items():
            #logging.info(f"######## Meta_data: {key} => {value}")
            if key in json_data:
                value_original = json_data[key]
                if value_original != value:
                    logging.info(f"Cambia: {key} de {value_original} a {value}")
                    json_data[key] = value
        #logging.info(f"######## Request Salida: {json_data}")
        return json_data

    def requestProcess(self, request, subpath ) :
            logging.info("===================================== INIT ==========================================================" )
            logging.info("Reciv " + str(request.method) + " Contex: " + str(subpath) )
            #logging.info("Reciv Header : " + str(request.headers) )
            logging.info("Reciv Data: " + str(request.data) )
            config = self.get_config()
            #logging.info("######## Config: " + str(config) )
            url = config['url'] + str(subpath)
            key = self.get_key_by_path(config, subpath)
            # si est'a habilitado el cache, se compara el hash
            if( config['enabled'] and subpath.find('rating/api/v1.0/rates/business') >= 0 ) :   
                logging.info("Cache habilitado, se compara el hash " ) 
                # reemplazamos los metadatos
                hash : str = str(hashlib.md5(request.data).hexdigest())
                if hash != None and hash == config['hash'] :
                    data_response = config['response']
                    json_data = json.dumps(data_response)
                    logging.info("Se responde el cache OK: " + json.loads(json_data) ) 
                    return json.loads(json_data), 200
                else: 
                    logging.info("No se responde el cache, se sigue !! " )

            headers = {'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/json' }
            # valores por defecto
            data_response = jsonify({'statusCode': 500, 'statusDescription': 'Error interno Gw' })
            errorCode = 500
            try :
                m1 = time.monotonic()
                resp = None
                if (request.method == 'POST' ) :
                    logging.info("URL : " + url )
                    data_request = self.procces_meta_data(config['meta_data'], request.get_json() )
                    resp = requests.post(url, json = data_request, headers = headers, timeout = 40)
                    diff = time.monotonic() - m1;

                if (request.method == 'PUT' ) :
                    logging.info("URL : " + url )
                    resp = requests.put( url, json = data_request, headers = headers, timeout = 40)
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
                            # url = url.replace('/v2', '')
                    # se reevia la peticion
                    logging.info("URL : " + url )
                    resp = requests.get(url, data = request.data, headers = headers, timeout = 40)
                    diff = time.monotonic() - m1;
                errorCode = resp.status_code
                logging.info("Key         : " + str(key) )
                
                if( resp.status_code == 200 ) :
                    data_response = resp.json()
                    logging.info("Response CXP OK: " + str( data_response ) )
                    # se actualiza en la BD s'olo si esta habilitado
                    if config['enabled'] and subpath.find('rating/api/v1.0/rates/business') >= 0 :
                        hash : str = str(hashlib.md5(request.data).hexdigest())
                        self.saveCache( str(request.get_json()), hash, str(data_response), config['id'] )

                else :
                    data_response = resp.json()
                    logging.info("Response CXP NOK[" + str(resp.status_code) + "]: " + str( data_response ) )

                logging.info("Time Response in " + str(diff) + " sec." )

            except Exception as e:
                print("ERROR POST:", e)
            
            logging.info("===================================== END ==========================================================" )
            return data_response, errorCode
