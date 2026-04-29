#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import time
    import requests
    import json
    from flask import Flask, render_template, abort, make_response, request, redirect, jsonify, send_from_directory
    # Clases personales

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['[Captcha] Error al buscar los modulos:',
                                 str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

ROOT_DIR = os.path.dirname(__file__)

SUCCESS_MSG = "Servicio ejecutado con exito"
SUCCESS_CODE = 0


class Captcha :
    root_dir = None
    google_secret = None
    def __init__(self, root_dir = str(ROOT_DIR)) :
        try:
            self.root_dir = root_dir
            self.google_secret = os.environ.get('RECAPTCHA_SECRET_KEY','NO_SECRET_KEY')
        except Exception as e :
            print("ERROR :", e)
            self.root_dir = None
            self.google_secret = None

    def __del__(self):
        self.root_dir = None
        self.google_secret = None

    def hcaptcha_process(self, json_data ) :
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }

        token = str(json_data['token'])
        secret = str(json_data['secret'])
        sitekey = str(json_data['sitekey'])

        logging.info("token recibido de largo " + str(len(token)) )
        diff = 0
        m1 = time.monotonic()
        data_response = {}
        code = 409
        if token != 'None' and secret != 'None' and sitekey != 'None':
            url = 'https://hcaptcha.com/siteverify'
            datos = {'secret': secret,'response': token,'sitekey': sitekey }
            # logging.info("URL : " + url )
            resp = requests.post(url, data = datos, headers = headers, timeout = 40)
            diff = time.monotonic() - m1
            code = resp.status_code
            if( resp.status_code == 200 ) :
                data_response = resp.json()
                logging.info("Response OK: " + str( data_response ) )
            else :
                data_response = resp.json()
                logging.info("Response NOK: " + str( data_response ) )

        logging.info("Time Response in " + str(diff) + " sec." )
        return data_response, code 

    def google_captcha( self, request) :
        token = str(request.args.get('token', 'None'))
        headers = { 'Content-Type': 'application/json' }
        logging.info("token reccibido de largo " + str(len(token)) )
        diff = 0
        m1 = time.monotonic()
        data_response = {}
        code = 409
        if token != 'None' and self.google_secret :
            url = 'https://www.google.com/recaptcha/api/siteverify?secret='+str(self.google_secret)+'&response='+token
            # logging.info("URL : " + url )
            resp = requests.get(url, data = request.data, headers = headers, timeout = 40)
            diff = time.monotonic() - m1
            code = resp.status_code
            if( resp.status_code == 200 ) :
                data_response = resp.json()
                logging.info("Response OK: " + str( data_response ) )
            else :
                data_response = resp.json()
                logging.info("Response NOK: " + str( data_response ) )
        logging.info("Time Response in " + str(diff) + " sec." )

        return data_response, code 
