try:
    import logging
    import sys
    import os
    import pymysql.cursors
    from datetime import datetime
    import time
    from utils import Cipher
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as ec
    from werkzeug.security import generate_password_hash, check_password_hash
    from flask import send_from_directory, jsonify

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[GranLogia] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class GranLogia () :
    logia_api_key = None
    root_dir = None
    def __init__(self, root_dir = '.') :
        try:
            self.root_dir = root_dir
            self.logia_api_key = str(os.environ.get('LOGIA_API_KEY','None'))
        except Exception as e :
            print("ERROR :", e)
            self.logia_api_key = None
            self.root_dir = None

    def __del__(self):
        self.logia_api_key = None
        self.root_dir = None

    def request_process(self, request, subpath ) :        
        data_response = jsonify({"message" : "No autorizado"})
        http_code  = 401

        logging.info("Reciv " + str(request.method) + " Contex: " + str(subpath) )
        logging.info("Reciv Header : " + str(request.headers) )
        logging.info("Reciv Data: " + str(request.data) )
        # evlua pai key inmediatamente
        apy_key = request.headers.get('API-Key')
        if str(apy_key) != str(self.logia_api_key) :
            return  data_response, http_code
        request_data = request.get_json()
        # se decifra el payload que llega si existe
        cipher = Cipher()
        data_clear = None
        if request_data['data'] != None and request.method == 'POST' :
            data_cipher = str(request_data['data'])
            logging.info('API Key Ok, Data Recibida: ' + data_cipher )
            data_bytes = cipher.aes_decrypt(data_cipher)
            if data_clear != None :
                data_clear = str(data_bytes.decode('UTF-8'))

        if request.method == 'POST' :
            if str(subpath).find('usergl/login') >= 0 :
                user = name = grade = None
                if data_clear != None :
                    datos = data_clear.split('|||')
                    if len(datos) == 2 and datos[0] != None and datos[1] != None :
                        user = str(datos[0]).strip()
                        passwd = str(datos[1]).strip()
                        if user != '' and passwd != '' :
                            gl = GranLogia()
                            name, grade, message, code  = gl.loginSystem( user, passwd )
                            del gl
                data_response = jsonify({
                    'message' : str(message),
                    'user' : str(user),
                    'grade' : str(grade),
                    'name' : str(name)
                })
            elif str(subpath).find('usergl/access') >= 0 :
                if data_clear != None :
                    datos = data_clear.split('&&')
                    if len(datos) == 2 and datos[0] != None and datos[1] != None :
                        user = str(datos[0]).strip()
                        grade = str(datos[1]).strip()
                        if user != '' and grade != '' :
                            gl = GranLogia()
                            message, code, http_code  = gl.validateAccess( user, grade )
                            del gl
                            data_response = jsonify({
                                'message' : str(message),
                                'code' : str(code)
                            })
            elif str(subpath).find('usergl/grade') >= 0 :
                if data_clear != None :
                    user = data_clear.strip()
                    if user != '' :
                        gl = GranLogia()
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
                            gl = GranLogia()
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
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD_LOGIA','None')
    password = os.environ.get('PASS_BD_LOGIA','None')
    database = 'gral-purpose'

    driver = None
    hub = str(os.environ.get('HUB_SELENIUM_URL','None')) + '/wd/hub'
    wait = None

    def __init__(self) :
        try:
            self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
            logging.info("HUB: " + self.hub)

        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def __del__(self):
        if self.db != None:
            self.db.close()
        if self.driver != None:
            self.driver.quit()

    def connect( self ) :
        try:
            if self.db == None :
                self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def isConnect(self) :
        return self.db != None

    def create_sesion(self):
        try:
            if self.hub != None :
                logging.info("Remote HUB: " + self.hub)
                self.driver = webdriver.Remote(self.hub, desired_capabilities=webdriver.DesiredCapabilities.CHROME)
                self.wait = WebDriverWait(self.driver, 30)  # 30 segundos
        except Exception as e:
            self.driver = None
            logging.warning("ERROR :", e) 

    def get_driver(self):
        if self.driver == None :
            self.create_sesion()
        return self.driver

    # se realiza el login y de acuerdo a los menus se detecta el grado del QH
    def login(self, username, password):
        grade = 1 # Inicialmente es Aprendiz
        browser = self.get_driver()
        name = 'Desconocido'
        try:
            logging.info("Login..")
            browser.get('https://www.mimasoneria.cl/web/login')
            rut_user = browser.find_element(By.ID, 'login')
            rut_user.send_keys(username)
            pswd = browser.find_element(By.ID,'password')
            pswd.send_keys(password)
            element = browser.find_element(By.XPATH, "//div[3]/button")
            logging.info("Se presiona boton entrar")
            element.click()
        except Exception as e:
            try:
                browser.save_screenshot(os.path.join("./", "login_error.png"))
                print('ERROR: ', e)
                grade = 0
            except:
                pass
        try:
            logging.info("Verifico si entre...")
            browser.save_screenshot(os.path.join("./", "paso 1.png"))
            # browser.execute_script("window.scrollTo(0, 0);")
            element = self.wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@id='custom_nav_chico']/nav/ul[2]/li/a/b/span")))
            name = str(element.text.strip())
            logging.info("Loging [Ok], Nombre: " + str(name) )
            oneandtwo =  name.split(' ')
            name = str(oneandtwo[0]) + ' ' + str(oneandtwo[1])
            grade = 1
            # me dirijo a la biblioteca
            element = self.wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@id='wrap']/div[2]/div[2]/div[3]/a/div/p")))
            element.click()

        except Exception as e:
            print("ERROR, no se pudo hacer login ", e)
            grade = 0
            try:
                browser.save_screenshot(os.path.join("./", "login_error.png"))
            except:
                pass

        if grade == 1 :
            try :
                element = browser.find_element(By.XPATH, "//img[@alt='Biblioteca Compañeros']")
                grade = 2
                logging.info("Se detecta que es grado 2")
            except Exception as e:
                print('No se encuentra indicios de ser compañero: ', e)

        if grade == 2 :
            try :
                element = browser.find_element(By.XPATH, "//img[@alt='Biblioteca Maestros']")
                grade = 3
                logging.info("Se detecta que es grado 3")
            except Exception as e:
                print('No se encuentra indicios de ser maestro: ', e)

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
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from secure where username = %s"""
                cursor.execute(sql, (username))
                results = cursor.fetchall()
                for row in results:
                    grade = int(row['grade'])
                    if grade > 0 and grade <=3 :
                        message = 'Servicio ejecutado exitosamente'
                        http_code = 200
        except Exception as e:
            print("ERROR BD:", e)

        logging.info('Message: ' + str(message) + ' para ' + str(username) )
        return message, grade, http_code

    #================================================================================================
    # Valido el grado del QH logeado con el del documento que desea ver
    #================================================================================================
    def validateAccess(self, username, grade) :
        logging.info('Valido acceso de usuario: ' + str(username)  + ' a cosas de ' + str(grade))
        message = "Usuario no autorizado"
        code  = -1
        http_code = 401
        grade_doc = int(grade)
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from secure where username = %s"""
                cursor.execute(sql, (username))
                results = cursor.fetchall()
                for row in results:
                    grade_qh = int(row['grade'])
                    if grade_doc <= grade_qh :
                        code = 4500
                        message = 'Usuario es de grado ' + str(grade_qh)
                        http_code = 200
        except Exception as e:
            print("ERROR BD:", e)

        logging.info(str(username)  + ' ' + str(message))
        return message, code, http_code

    def verifiyUserPass( self, username, password ) :
        logging.info("Rescato password para usuario: " + str(username) )
        passwordBd = None
        userResp = None
        grade = 0
        name = ''
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from secure where username = %s"""
                cursor.execute(sql, (username))
                results = cursor.fetchall()
                passwordBd = None
                userBd = None
                # saco los datos de la BD
                for row in results :
                    passwordBd = str(row['password'])
                    userBd = str(row['username'])
                    name = str(row['name'])
                    grade = int(str(row['grade']))
                    logging.info("Usuario " + str(name) + " encontrado")
                # guardo lo que se necesita y solo si existen ambos valores
                if userBd != None and passwordBd != None :
                    check = check_password_hash(passwordBd, password ) 
                    if userBd.strip() == username.strip() and check :
                        logging.info("Usuario " + str(username) + " validado Ok")
                        userResp = userBd.strip()
                    else :
                        logging.info("Ckeck: " + str(check)+ " Error validando passwd de " + str(username) ) 
                        grade = 0
                        name = ''
                else :
                  logging.info('user y/o password no encontrado')  
                  grade = 0
                  name = ''
        except Exception as e:
            print("ERROR BD:", e)
        return userResp, grade, name


    def loginSystem(self, username, password) :
        logging.info("Verifico Usuario: " + str(username) )
        message = "Ok"
        code = 200
        user, saved_grade, name_saved = self.verifiyUserPass( username, password )
        if user == None :
            grade, name_saved = self.login( username, password )
            logging.info("Nombre: " + str(name_saved) + "Grade: " + str(grade) )
            if grade > 0 and grade < 4 :
                try :
                    if self.db != None :
                        cursor = self.db.cursor()
                        sql = """INSERT INTO secure (date_save, username, password, grade, name ) VALUES(%s, %s, %s, %s, %s)"""
                        now = datetime.now()
                        cursor.execute(sql, (now.strftime("%Y-%m-%d %H:%M:%S"), username, generate_password_hash(password), grade, name_saved ))
                        self.db.commit()
                        message = 'Usuario Creado'
                        code = 201
                        saved_grade = int(grade)
                except Exception as e:
                    print("ERROR BD:", e)
                    self.db.rollback()
                    message = "Error en BD"
                    code = 500
                    saved_grade = 0
                    name_saved = ''
            else :
                message = "El usuario es inválido"
                code = 409
        return name_saved, saved_grade, message, code 
    