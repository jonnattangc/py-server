try:
    import logging
    import sys
    import os
    import pymysql.cursors
    from datetime import datetime
    import time
    from utils import Cipher
    from flask import send_from_directory, jsonify
    import requests
    import json

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[GranLogia] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class GranLogia () :
    root_dir = None
    def __init__(self, root_dir = '.') :
        try:
            self.root_dir = root_dir 
        except Exception as e :
            print("ERROR :", e)
            self.root_dir = None

    def __del__(self):
        self.root_dir = None

    def request_process(self, request, subpath ) :        
        data_response = jsonify({"message" : "No autorizado"})
        http_code  = 401

        logging.info("Reciv " + str(request.method) + " Contex: " + str(subpath) )
        logging.info("Reciv Header : " + str(request.headers) )
        logging.info("Reciv Data: " + str(request.data) )
        # evlua api-key inmediatamente
        logia_api_key = str(os.environ.get('LOGIA_API_KEY','None'))
        api_key = request.headers.get('API-Key')
        if str(api_key) != str(logia_api_key) :
            return  data_response, http_code
        request_data = request.get_json()
        # se decifra el payload que llega si existe
        cipher = Cipher()
        data_clear = None
        if request_data['data'] != None and request.method == 'POST' :
            data_cipher = str(request_data['data'])
            logging.info('API Key Ok, Data Recibida: ' + data_cipher )
            data_clear = cipher.aes_decrypt(data_cipher)

        if request.method == 'POST' :
            if str(subpath).find('usergl/login') >= 0 :
                user = name = grade = None
                message = None
                if data_clear != None :
                    datos = data_clear.split('|||')
                    if len(datos) == 2 and datos[0] != None and datos[1] != None :
                        user = str(datos[0]).strip()
                        passwd = str(datos[1]).strip()
                        if user != '' and passwd != '' :
                            scraper = Selenium()
                            name, grade, message, code  = scraper.login_system( user, passwd )
                            del scraper
                            data_response = jsonify({
                                'message' : str(message),
                                'user' : str(user),
                                'grade' : str(grade),
                                'name' : str(name)
                            })
                            http_code = 200
            elif str(subpath).find('usergl/access') >= 0 :
                if data_clear != None :
                    datos = data_clear.split('&&')
                    if len(datos) == 2 and datos[0] != None and datos[1] != None :
                        user = str(datos[0]).strip()
                        grade = str(datos[1]).strip()
                        if user != '' and grade != '' :
                            scraper = Selenium()
                            message, code, http_code  = scraper.validate_access( user, grade )
                            del scraper
                            data_response = jsonify({
                                'message' : str(message),
                                'code' : str(code)
                            })
            elif str(subpath).find('usergl/grade') >= 0 :
                if data_clear != None :
                    user = data_clear.strip()
                    if user != '' :
                        gl = Selenium()
                        message, grade, http_code  = gl.getGrade( user )
                        del gl
                        data_response = jsonify({
                            'message' : str(message),
                            'grade' : str(grade)
                        })
            elif str(subpath).find('docs/url') >= 0 :
                if data_clear != None :
                    datos = data_clear.split(';')
                    if len(datos) == 3 and datos[0] != None and datos[1] != None and datos[2] != None :
                        name_doc = str(datos[0]).strip()
                        grade_doc = str(datos[1]).strip()
                        id_qh = str(datos[2]).strip()
                        if name_doc != '' and grade_doc != '' and id_qh != '' :
                            gl = Selenium()
                            message, code, http_code  = gl.validateAccess( id_qh, grade_doc )
                            del gl
                            if code != -1 and message != None and http_code == 200 :
                                url_doc = 'https://dev.jonnattan.com/logia/docs/pdf/' + str(time.monotonic_ns()) + '/'
                                logging.info('URL Base: ' + str(url_doc) )
                                data_cipher = cipher.aes_encrypt( name_doc )
                                data_response = jsonify({
                                    'data' : str(data_cipher.decode('UTF-8')),
                                    'url'  : str(url_doc)
                                })
            else: 
                data_response = jsonify({"message" : "No procesado el contexto: " + str(subpath)})
                http_code = 404
        elif request.method == 'GET' :
            if str(subpath).find('docs/pdf') >= 0 :
                file_path = os.path.join(self.root_dir, 'static/logia')
                route = subpath.replace('docs/pdf', '')
                paths = str(route).split('/')
                if len(paths) == 2 :
                    mark = int(str(paths[0]).strip())
                    diff = time.monotonic_ns() - mark
                    logging.info("DIFFFFFF: " + str(diff))
                    if diff < 1000000000 :
                        data_bytes = cipher.aes_decrypt(str(paths[1]).strip())
                        data_clear = str(data_bytes.decode('UTF-8'))
                        logging.info("Find File: " + str(data_clear))
                        data_response = send_from_directory(file_path, data_clear)
                        http_code = 200
            elif str(subpath).find('images') >= 0 :
                fromHost = request.headers.get('Referer')
                if fromHost != None :
                    if str(fromHost).find('https://logia.buenaventuracadiz.com') >= 0 :
                        file_path = os.path.join(self.root_dir, 'static')
                        file_path = os.path.join(file_path, 'images')
                        data_response =  send_from_directory(file_path, str(name) )
                        http_code = 200
        del cipher
        return  data_response, http_code
    

class Selenium() :
    logia_api_key = None
    root_dir = None
    base_url = None
    cipher = None
    headers = None 
    def __init__(self, root_dir = '.') :
        try:
            self.root_dir = root_dir
            self.logia_api_key = str(os.environ.get('LOGIA_API_KEY','None'))
            self.base_url = str(os.environ.get('LOGIA_BASE_URL','None'))
            self.cipher = Cipher()
            self.headers = {
                'Accept': 'application/json', 
                'Content-Type': 'application/json',
                'x-api-key': str(self.logia_api_key),
                'Authorization': 'Basic am9ubmF0dGFuOndzeHphcTEyMw=='
            }

        except Exception as e :
            print("ERROR :", e)
            self.logia_api_key = None
            self.root_dir = None
            self.base_url = None
            self.cipher = None
            self.headers = None 

    def __del__(self):
        self.logia_api_key = None
        self.root_dir = None
        self.base_url = None
        del self.cipher
        self.cipher = None
        self.headers = None 

    # se realiza el login y de acuerdo a los menus se detecta el grado del QH
    def login(self, username, password):
        grade = 1 # Inicialmente es Aprendiz
        name = 'Desconocido'
        try :
            url = self.base_url + '/logia/login'
            data = username + '|||' + password
            data_cipher = self.cipher.aes_encrypt(data)
            datos = {'data': data_cipher }
            resp = requests.post(url, data = json.dumps(datos), headers = self.headers, timeout = 40)
            code = resp.status_code
            if( resp.status_code == 200 ) :
                data_response = resp.json()
                logging.info("Response OK: " + str( data_response ) )
                grade = int(data_response['grade'])
                name = str(data_response['name'])
        except Exception as e:  
            print("[Selenium] ERROR Login: ", e)
        logging.info('El QH ' + str(name) + ' es del grado: ' + str(grade) )
        return grade, name

    #================================================================================================
    # obtiene grado del qh
    #================================================================================================
    def getGrade(self, username ) :
        logging.info('Obtiene grado de: ' + str(username))
        message = "Usuario no existe"
        grade  = 0
        http_code = 409
        try :
            url = self.base_url + '/logia/grade'
            data_cipher = self.cipher.aes_encrypt(username)
            datos = {'data': data_cipher }
            resp = requests.post(url, data = json.dumps(datos), headers = self.headers, timeout = 40)
            code = resp.status_code
            if( resp.status_code == 200 ) :
                data_response = resp.json()
                logging.info("Response OK: " + str( data_response ) )
                grade = int(data_response['grade'])
                message = str(data_response['message'])
        except Exception as e:
            print("ERROR BD:", e)

        logging.info('Message: ' + str(message) + ' para ' + str(username) )
        return message, grade, http_code

    #================================================================================================
    # Valido el grado del QH logeado con el del documento que desea ver
    #================================================================================================
    def validate_access(self, username: str, grade: str) :
        logging.info('Valido acceso de usuario: ' + str(username)  + ' a cosas de ' + str(grade))
        message = "Usuario no autorizado"
        code  = -1
        http_code = 401
        try :
            url = self.base_url + '/logia/access'
            data_cipher = self.cipher.aes_encrypt(username)
            data = username + '&&' + grade
            data_cipher = self.cipher.aes_encrypt(data)
            datos = {'data': data_cipher }
            resp = requests.post(url, data = json.dumps(datos), headers = self.headers, timeout = 40)
            http_code = resp.status_code
            if( resp.status_code == 200 ) :
                data_response = resp.json()
                logging.info("Response OK: " + str( data_response ) )
                code = int(data_response['code'])
                message = str(data_response['message'])
        except Exception as e:
            print("ERROR BD:", e)

        logging.info(str(username)  + ' ' + str(message))
        return message, code, http_code

    def login_system(self, username, password) :
        logging.info("Verifico Usuario: " + str(username) )
        message = "Ok"
        code = 200
        saved_grade, name_saved = self.login( username, password )
        logging.info("Nombre: " + str(name_saved) + " Grade: " + str(saved_grade) )
        if int(saved_grade) > 0 and int(saved_grade) < 4 :
            logging.info('Obtiene grado de: ' + str(username))
        else :
            message = "El usuario es inválido"
            code = 409
        return name_saved, saved_grade, message, code 
    