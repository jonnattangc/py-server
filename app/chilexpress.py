try:
    import logging
    import sys
    import os
    import time
    import json
    import requests
    import pymysql.cursors
    from datetime import datetime, timedelta
    from flask import Flask, render_template, abort, make_response, request, redirect, jsonify, send_from_directory
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class Chilexpress() :
    db = None
    host = '192.168.0.15'
    user = 'jonnattan'
    password = 'wsxzaq123'
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
                if( subpath.find('rating/') >= 0 ) :
                    key = 'fd46aa18a9fe44c6b49626692605a2e8'
                if( subpath.find('transport-orders/') >= 0 ) :
                    key = '0112f48125034f8fa42aef2441773793'

            if( currentEnv.find('qa') >= 0 ) :
                url = 'https://qaservices.wschilexpress.com/' + str(subpath)
                if( subpath.find('rating/') >= 0 ) :
                    key = 'eb5a6789c2424b7bbe1520b4c56b747c'
                if( subpath.find('transport-orders/') >= 0  ) :
                    key = '389afe5ba86d4d54b6a62d37726cb4d2'
                if( subpath.find('georeference/') >= 0  ) :
                    key = 'd0b39697973b41a4bb1e0bc3e0eb625c'


            logging.info("Environment : " + str(currentEnv) )
            logging.info("Key : " + key )
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
                    region = request.args.get('RegionCode', '-1')
                    tipo = request.args.get('type', '-1')
                    if ( region != '-1' and tipo != '-1' ) :
                        url = url + "?RegionCode=" + region + "&type=" + tipo
                    logging.info("URL : " + url )
                    resp = requests.get(url, data = request.data, headers = headers, timeout = 40)
                    diff = time.monotonic() - m1;
                errorCode = resp.status_code
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
