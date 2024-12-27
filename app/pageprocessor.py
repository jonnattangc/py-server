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
    from security import Security
    from sserpxelihc import Sserpxelihc
    from memorize import Memorize
    from utilaws import AwsUtil
    from utilwaza import UtilWaza
    from utilgeo import GeoPosUtil
    from utilattlasian import UtilAttlasian
    from captcha import Captcha
    from utils import Banks, Cipher

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['[http-server] Error al buscar los modulos:',
                                 str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

ROOT_DIR = os.path.dirname(__file__)

SUCCESS_MSG = "Servicio ejecutado con exito"
SUCCESS_CODE = 0

class Page : 
    root_dir = None
    api_key = None
    cipher = None
    def __init__(self, root_dir = str(ROOT_DIR)) :
        try:
            self.root_dir = root_dir
            self.api_key = str(os.environ.get('PAGE_API_KEY','None'))
            self.base_url = str(os.environ.get('LOGIA_BASE_URL','None'))
            self.cipher = Cipher()
        except Exception as e :
            print("ERROR :", e)
            self.api_key = None
            self.root_dir = None
            self.cipher = None

    def __del__(self):
        self.root_dir = None
        self.api_key = None
        del self.cipher
        self.cipher = None

    def request_process(self, request, subpath ) :
        data_response = {"message" : "No autorizado", "code": 401, "data": None}
        http_code  = 401
        json_data = None

        logging.info("Reciv " + str(request.method) + " Contex: /page/" + str(subpath) )
        #logging.info("Reciv Header : " + str(request.headers) )
        #logging.info("Reciv Data: " + str(request.data) )

        rx_api_key = request.headers.get('x-api-key')
        if str(rx_api_key) != str(self.api_key) :
            return  data_response, http_code
        
        request_data = None 
        request_type = None
        data_rx = None
        if request.data != None and len(request.data) > 0:
            request_data = request.get_json()
            try :
                request_type = request_data['type']
            except Exception as e :
                request_type = None
            try :
                data_rx = request_data['data']
            except Exception as e :
                data_rx = None

        if request_type != None :
            if data_rx != None and str(request_type) == 'encrypted' and request.method == 'POST' :
                data_cipher = str(data_rx)
                #logging.info('Data Encrypt: ' + str(data_cipher) )
                data_clear = self.cipher.aes_decrypt(data_cipher)
                #logging.info('Data EnClaro: ' + str(data_clear) )
                json_data = json.dumps(data_clear)
            else: 
                json_data = data_rx
        else: 
                json_data = data_rx

        logging.info("JSON: " + str(json_data) )

        if request.method == 'POST' :
            if str(subpath).find('hook') >= 0 :
                data, http_code = self.hook_process( json_data )
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
            elif str(subpath).find('geo/') >= 0 :
                path = str(subpath).replace('geo/', '')
                util = GeoPosUtil(root = self.root_dir)
                data, http_code = util.request_process( request, path )
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
                del util
            elif str(subpath).find('aws/') >= 0 :
                action = str(subpath).replace('aws/', '')
                aws = AwsUtil(root = self.root_dir)
                data, http_code = aws.request_process( request, str(action) )
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
                del aws
            elif str(subpath).find('hcaptcha/') >= 0 :
                hcaptcha = Captcha()
                data, http_code = hcaptcha.hcaptcha_process( json_data )
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
                del hcaptcha
            elif str(subpath).find('attlasian/') >= 0 :
                util = UtilAttlasian()
                data, http_code = util.requestProcess(request, subpath)
                del util
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
            elif str(subpath).find('memorize/') >= 0 :
                action = str(subpath).replace('memorize/', '')
                data, http_code = self.memorize_process(request, action)
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
            elif str(subpath).find('waza/') >= 0 :
                action = str(subpath).replace('waza/', '')
                data, http_code = self.waza_process(request, action)
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
            elif str(subpath).find('cxp/') >= 0 :
                action = str(subpath).replace('cxp/', '')
                cxp = Sserpxelihc()
                data, http_code = cxp.requestProcess(request, action)
                del cxp
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
            else: 
                data_response = {"message" : "Servicio POST no encontrado", "code": 404, "data": None}
                http_code  = 404

        elif request.method == 'GET' :
            if str(subpath).find('docs/') >= 0 :
                name_file = str(subpath).replace('docs/', '')
                data_response, http_code = self.docs_process(name_file)
            elif str(subpath).find('aws/') >= 0 :
                action = str(subpath).replace('aws/', '')
                aws = AwsUtil(root = self.root_dir)
                data, http_code = aws.request_process(request, str(action))
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
                del aws
            elif str(subpath).find('recaptcha/') >= 0 :
                recaptcha = Captcha()
                data, http_code = recaptcha.google_captcha( request )
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
                del recaptcha
            elif str(subpath).find('cv/') >= 0 :
                action = str(subpath).replace('cv/', '')
                data, http_code = self.cv_proccess( action )
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
            elif str(subpath).find('memorize/') >= 0 :
                action = str(subpath).replace('memorize/', '')
                data, http_code = self.memorize_process(request, action)
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
            elif str(subpath).find('image/') >= 0 :
                name_file = str(subpath).replace('image/', '')
                data_response, http_code = self.image_process(name_file)
            elif str(subpath).find('js/') >= 0 :
                name_file = str(subpath).replace('js/', '')
                data_response, http_code = self.js_process(name_file)
            elif str(subpath).find('usergenerate/') >= 0 :
                basicAuth = Security()
                basicAuth.generateUser('jonnattan', 'wsxzaq123')
                del basicAuth
                http_code = 201
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": {} }
            elif str(subpath).find('cxp/change/') >= 0 :
                env = str(subpath).replace('cxp/change/', '')
                cxp = Sserpxelihc()
                old, success = cxp.saveEnv(str(env))
                http_code = 400
                data = {
                    'old'   : old,
                    'to'    : str(env),
                    'change': success
                }
                if success : 
                    http_code = 200
                del cxp
                data_response = {"message" : SUCCESS_MSG, "code": SUCCESS_CODE, "data": data }
            else :
                data_response = {"message" : "Servicio GET no encontrado", "code": 404, "data": None}
                http_code  = 404

        return  data_response, http_code


    def memorize_process( self, request, action: str ) :
        memo = Memorize()
        data = None
        http_code = 200 

        if action.find('reset/') >= 0 :
            data, http_code = memo.resetProcess()
        if action.find('save/') >= 0 :
            data, http_code =  memo.requestProcess(request)
        if action.find('states/') >= 0 :
            names, states = memo.getState()
            del memo
            data = []
            i = 0
            for name in names :
                data.append({
                    'name': name,
                    'state': states[i]
                })
                i = i + 1
        return data, http_code

    def waza_process(self, request, subpath ) :
        waza = UtilWaza( self.root_dir )
        msg, code = waza.requestProcess(request, subpath)
        del waza
        return msg, code

    def hook_process(self, data ) :
        return {message:"Servicio exitoso", "code": 0, "data": None}, 200
    

    def docs_process(self, path ) :
        file_path = os.path.join(self.root_dir, 'static')
        file_path = os.path.join(file_path, 'docs')
        return send_from_directory( file_path, str(path) ), 200
    

    def image_process(self, path ) :
        file_path = os.path.join(self.root_dir, 'static')
        file_path = os.path.join(file_path, 'images')
        return send_from_directory( file_path, str(path) ), 200
    

    def js_process(self, path ) :
        file_path = os.path.join(self.root_dir, 'static')
        file_path = os.path.join(file_path, 'js')
        return send_from_directory( file_path, str(path) ), 200
    
    def cv_proccess( self, subpath ) :
        data_response = {}
        code = 200
        try :
            if subpath != None and subpath.find('/') < 0 and len(subpath) > 0 :
                logging.info("Obtengo CV de: " + str(subpath) )
                file_path = os.path.join(self.root_dir, 'static')
                file_path = os.path.join(file_path, 'cvs')
                file_path = os.path.join(file_path, str(subpath) + '_cv.data')
                with open(file_path) as file:
                    data_cv = file.read()
                    file.close()
        except Exception as e:
            print("ERROR process_cv() :", e)
            data_response = {}
            code = 401
        data_response = {
            "name": "Jonnattan Griffiths",
            "data": str(data_cv)
        }
        return data_response, code