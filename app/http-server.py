#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import time
    import requests
    import json
    from flask_cors import CORS
    from flask_wtf.csrf import CSRFProtect
    from flask_httpauth import HTTPBasicAuth
    from flask_login import LoginManager, UserMixin, current_user, login_required, login_user
    from flask import Flask, render_template, abort, make_response, request, redirect, jsonify, send_from_directory
    from coordinator import Coordinator
    from security import Security
    from check import Checker
    from dernede import Dernede
    from memorize import Memorize
    from granl import GranLogia
    from utilwaza import UtilWaza
    from ucc import Ucc
    from pageprocessor import Page

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['[http-server] Error al buscar los modulos:',
                                 str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

############################# Configuraci'on de Registro de Log  ################################
FORMAT = '%(asctime)s %(levelname)s : %(message)s'
root = logging.getLogger()
root.setLevel(logging.INFO)
formatter = logging.Formatter(FORMAT)
# Log en pantalla
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
#fh = logging.FileHandler('logger.log')
#fh.setLevel(logging.INFO)
#fh.setFormatter(formatter)
# se meten ambas configuraciones
root.addHandler(handler)
#root.addHandler(fh)

logger = logging.getLogger('HTTP')
# ===============================================================================
# Configuraciones generales del servidor Web
# ===============================================================================


SECRET_CSRF = os.environ.get('SECRET_KEY_CSRF','KEY-CSRF-ACA-DEBE-IR')

app = Flask(__name__)
app.config.update( DEBUG=False, SECRET_KEY = str(SECRET_CSRF), )

#login_manager = LoginManager()
#login_manager.init_app(app)

csrf = CSRFProtect()
csrf.init_app(app)

auth = HTTPBasicAuth()
# cors = CORS(app, resources={r"/page/*": {"origins": ["*"]}})
cors = CORS(app, resources={r"/page/*": {"origins": ["dev.jonnattan.com"]}})
# ===============================================================================
# variables globales
# ===============================================================================
ROOT_DIR = os.path.dirname(__file__)

#===============================================================================
# Redirige
#===============================================================================
@app.route('/', methods=['GET', 'POST'])
@csrf.exempt
def index():
    logging.info("Reciv solicitude endpoint: /" )
    return redirect('/infojonna'), 302

#===============================================================================
# Redirige
#===============================================================================
@app.route('/<path:subpath>', methods=('GET', 'POST'))
@csrf.exempt
def processOtherContext( subpath ):
    logging.info("Reciv solicitude endpoint: " + subpath )
    return redirect('/infojonna'), 302

#===============================================================================
# Redirige a mi blog personal
#===============================================================================
@app.route('/infojonna', methods=['GET', 'POST'])
@csrf.exempt
def infoJonnaProccess():
    logging.info("Reciv solicitude endpoint: /infojonna" )
    return jsonify({
        "Servidor": "dev.jonnattan.com",
        "Nombre": "Jonnattan Griffiths Catalan",
        "Linkedin":"https://www.linkedin.com/in/jonnattan/"
    })
#===============================================================================
# Metodo solicitado por la biblioteca de autenticaci'on b'asica
#===============================================================================
@auth.verify_password
def verify_password(username, password):
    user = None
    if username != None :
        basicAuth = Security()
        user =  basicAuth.verifiyUserPass(username, password)
        del basicAuth
    return user

#===============================================================================
# Implementacion del handler que respondera el error en caso de mala autenticacion
#===============================================================================
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'message':'invalid credentials'}), 401)

#===============================================================================
# Se checkea el estado del servidor completo para reportar
#===============================================================================
@app.route('/checkall', methods=['GET', 'POST'])
@auth.login_required
@csrf.exempt
def checkProccess():
    checker = Checker()
    json = checker.getInfo()
    del checker
    return jsonify(json)

# ==============================================================================
# Test con Edr
# ==============================================================================
@app.route('/dernede/<path:subpath>', methods=['GET', 'POST'])
@csrf.exempt
@auth.login_required
def dernedeProcess( subpath ):
    edr = Dernede(ROOT_DIR)
    dataTx, error = edr.requestProcess(request, subpath)
    del edr
    return dataTx, error

# ==============================================================================
# Para simular las respuesta de criptomkt.
# ==============================================================================
@app.route('/cmkt/<path:subpath>', methods=['GET', 'POST'])
@csrf.exempt
@auth.login_required
def crypto_mrk(subpath) :
    manager = Coordinator()
    dataTx, code_http = manager.proccess_solicitude( request, str( subpath) )
    del manager
    return jsonify(dataTx), code_http

# ==============================================================================
# Para simular las respuesta del casino deams
# ==============================================================================
@app.route('/dreams/<path:subpath>', methods=['GET', 'POST'])
@csrf.exempt
@auth.login_required
def sun_dreams( subpath ):
    manager = Coordinator()
    dataTx, code_http = manager.proccess_solicitude( request, '/dreams/' + str(subpath) )
    del manager
    return jsonify(dataTx), code_http

# ==============================================================================
# Tests UCC Relacionados con los contratos y la generaci'on de estos.
# ==============================================================================
@app.route('/ucc/<path:subpath>', methods=['GET', 'POST'])
@csrf.exempt
@auth.login_required
def proccess_ucc( subpath ):
    ucc = Ucc()
    data_response, http_code = ucc.request_process(request, str(subpath) )
    del ucc
    return data_response, http_code

# ==============================================================================
# Hook desde la API de Waza, no posee firma de nada y por lo tanto sin seguridad
# ==============================================================================
@app.route('/waza', methods=['POST','GET','PUT'])
@csrf.exempt
def wazasp( ):
    waza = UtilWaza( ROOT_DIR )
    msg, code = waza.requestProcess(request, None)
    del waza
    return msg, code

# ==============================================================================
# Procesa peticiones de la pagina de la logia
# ==============================================================================
@app.route('/logia/<path:subpath>', methods=['POST', 'GET'])
@csrf.exempt
def gran_logia_process(subpath):
    gl = GranLogia( ROOT_DIR )
    data, code = gl.request_process( request, subpath )
    del gl
    return data, code

# ==============================================================================
# Procesa solicitudes desde pagina web
# ==============================================================================
@app.get('/page')
@csrf.exempt
def page_page() :
    page = Page()
    data_response, http_status, is_page = page.request_process( request, "web" )
    del page
    if is_page:
        return data_response, http_status    
    else:
        return jsonify(data_response), http_status
@app.route('/page/<path:subpath>', methods=['GET','POST'])
@csrf.exempt
@auth.login_required
def process_page( subpath ):
    page = Page()
    data_response, http_status, is_page = page.request_process( request, str(subpath) )
    del page
    if is_page:
        return data_response, http_status    
    else:
        return jsonify(data_response), http_status

# ===============================================================================
# Favicon
# ===============================================================================
@app.route('/favicon.ico', methods=['POST','GET','PUT'])
@csrf.exempt
def favicon():
    file_path = os.path.join(ROOT_DIR, 'static')
    file_path = os.path.join(file_path, 'images')
    logging.info("Icono: " + str( file_path ) )
    return send_from_directory(file_path,
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ===============================================================================
# Metodo Principal que levanta el servidor
# ===============================================================================
if __name__ == "__main__":
    listenPort = 8085
    logger.info("ROOT_DIR: " + ROOT_DIR)
    logger.info("ROOT_DIR: " + app.root_path)
    if(len(sys.argv) == 1):
        logger.error("Se requiere el puerto como parametro")
        exit(0)
    try:
        logger.info("Server listen at: " + sys.argv[1])
        listenPort = int(sys.argv[1])
        # app.run(ssl_context='adhoc', host='0.0.0.0', port=listenPort, debug=True)
        # app.run( ssl_context=('cert_jonnattan.pem', 'key_jonnattan.pem'), host='0.0.0.0', port=listenPort, debug=True)
        app.run( host='0.0.0.0', port=listenPort)
    except Exception as e:
        print("ERROR MAIN:", e)

    logging.info("PROGRAM FINISH")
