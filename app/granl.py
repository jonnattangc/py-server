try:
    import logging
    import sys
    import os
    import time
    import pymysql.cursors
    from datetime import datetime
    # para hacer scraper
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as ec

    from werkzeug.security import generate_password_hash, check_password_hash

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class GranLogia() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD_LOGIA','None')
    password = os.environ.get('PASS_BD_LOGIA','None')
    database = 'gral-purpose'

    driver = None
    hub = None
    wait = None

    def __init__(self) :
        try:
            self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)

            self.hub = "http://192.168.0.15:4444/wd/hub"
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
                self.wait = WebDriverWait(self.driver, 60)  # 30 segundos
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
            logging.info("Loging...")
            browser.get('https://www.granlogiadechile.cl/index.php/login-user')
            rut_user = browser.find_element(By.ID, 'username')
            rut_user.send_keys(username)
            pswd = browser.find_element(By.ID,'password')
            pswd.send_keys(password)
            element = browser.find_element(By.XPATH, "//div[@id='sp-component']/div/div[2]/div/div/form/div[4]/button")
            logging.info("Se presiona btn entrar")
            element.click()
        except Exception as e:
            try:
                browser.save_screenshot(os.path.join("./", "login_error.png"))
                logging.info('ERROR: ', e)
                grade = 0
            except:
                pass
        try:
            logging.info("Verifico si entre...")
            browser.execute_script("window.scrollTo(0, 0);")
            element = self.wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@id='btl']/div/span")))
            name = str(element.text.strip())
            logging.info("Loging [Ok]")
            grade = 1
        except Exception as e:
            logging.info('ERROR, no se pudo hacer login ')
            grade = 0
            try:
                browser.save_screenshot(os.path.join("./", "login_error.png"))
            except:
                pass

        if grade == 1 :
            try :
                element = browser.find_element(By.XPATH, "//a[contains(text(),'Compañeros')]")
                grade = 2
                logging.info("Se detecta que es grado 2")
            except Exception as e:
                logging.info('No se encuentra indicios de ser compañero')

        if grade == 2 :
            try :
                element = browser.find_element(By.XPATH, "//a[contains(text(),'Maestros')]")
                grade = 3
                logging.info("Se detecta que es grado 3")
            except Exception as e:
                logging.info('No se encuentra indicios de ser maestro')

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
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from secure where username = %s"""
                cursor.execute(sql, (username))
                results = cursor.fetchall()
                passwordBd = None
                userBd = None
                # saco los datos de la BD
                for row in results:
                    passwordBd = str(row['password'])
                    userBd = str(row['username'])
                # guardo lo que se necesita y solo si existen ambos valores
                if userBd != None and passwordBd != None :
                    check = check_password_hash(passwordBd, password ) 
                    if userBd.strip() == username.strip() and check :
                        logging.info("Usuario " + str(username) + " validado Ok")
                        userResp = userBd.strip()
                    else :
                        logging.info("Ckeck: " + str(check)+ " Error validando passwd de " + str(username) ) 
                else :
                  logging.info('user y/o password no encontrado')  
        except Exception as e:
            print("ERROR BD:", e)
        return userResp


    def loginSystem(self, username, password) :
        logging.info("Verifico Usuario: " + str(username) )
        message = "Ok"
        code = 200
        user = self.verifiyUserPass( username, password )
        if user == None :
            grade, name = self.login( username, password)
            logging.info("Nombre: " + str(name) )
            if grade > 0 and grade < 4 :
                try :
                    if self.db != None :
                        cursor = self.db.cursor()
                        sql = """INSERT INTO secure (date_save, username, password, grade) VALUES(%s, %s, %s, %s)"""
                        now = datetime.now()
                        cursor.execute(sql, (now.strftime("%Y-%m-%d %H:%M:%S"), username, generate_password_hash(password), grade ))
                        self.db.commit()
                        message = 'Usuario Creado'
                        code = 201
                except Exception as e:
                    print("ERROR BD:", e)
                    self.db.rollback()
                    message = "Error en BD"
                    code = 500
            else :
                message = "El usuario es inválido"
                code = 409
        return message, code 