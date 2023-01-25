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


class Memorize() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
    database = 'proxy'

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
    def getState(self) :
        names = []
        states = []
        try :
            if self.isConnect() :
                cursor = self.db.cursor()
                sql = """select * from proxy where client = %s"""
                cursor.execute(sql, ('ionix-day'))
                results = cursor.fetchall()
                for row in results:
                    state = str(row['environment'])
                    name = str(row['name'])
                    states.append(state)
                    names.append(name)
                    # logging.info("Rescato card: " + name + " estado: " + state )
        except Exception as e:
            print("ERROR BD:", e)
        
        return names, states
# ==============================================================================
    def resetProcess(self ) :
        msg = 'Ha ocurrio un error'
        code = 500
        try :
            if self.isConnect() :
                cursor = self.db.cursor()
                sql = """UPDATE proxy set environment=%s where client=%s"""
                cursor.execute(sql, ('down', 'ionix-day'))
                self.db.commit()
                msg = 'Servicio Ejecutado exitosamente'
                code = 200
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
        return msg, code
# ==============================================================================
    def saveProcess(self, card, state) :
        msg = 'Ha ocurrio un error'
        code = 500
        try :
            if self.isConnect() :
                cursor = self.db.cursor()
                sql = """UPDATE proxy set environment=%s where client=%s and name=%s"""
                cursor.execute(sql, (state, 'ionix-day', card ))
                self.db.commit()
                msg = 'Servicio Ejecutado exitosamente'
                code = 200
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
        return msg, code
# ==============================================================================
    def requestProcess(self, request ) :
        logging.info("Reciv Data: " + str(request.data) )
        # logging.info("Reciv Header : " + str(request.headers) )
        request_data = request.get_json()
        return self.saveProcess( str(request_data['card']), str(request_data['state']))
