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
    # Clases personales
    from utils import Banks, Cipher
    from coordinator import Coordinator
    from security import Security
    from check import Checker
    from sserpxelihc import Sserpxelihc
    from dernede import Dernede
    from memorize import Memorize
    from granl import GranLogia
    from utilaws import AwsUtil
    from utilwaza import UtilWaza
    from utilgeo import GeoPosUtil
    from utilattlasian import UtilAttlasian
    from ucc import Ucc

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

SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY','NO_SECRET_KEY')
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

@app.route('/page/usergenerate', methods=['GET'])
@csrf.exempt
@auth.login_required
def usergeneratate(  ):
    basicAuth = Security()
    basicAuth.generateUser('jonnattan', 'wsxzaq123')
    del basicAuth
    json = {}
    return jsonify(json)

#===============================================================================
# Cualquier pagina que ocupe JS desde este servidor para por ac'a
#===============================================================================
@app.route('/page/js/<path:namejs>')
def process_jsfile( namejs ):
    file_path = os.path.join(ROOT_DIR, 'static')
    file_path = os.path.join(file_path, 'js')
    logging.info('Call JS File: ' + file_path + '/' + str(namejs) )
    return send_from_directory(file_path, str(namejs) )

#===============================================================================
# Formulario para probar los de CSFR Token Proteccion
#===============================================================================
@app.route('/page', methods=['GET'])
def test__form_csrf():
    logging.info("Pagina de edicion !! ")
    return render_template( 'create.html' )

@app.route('/page/csrf', methods=['POST'])
def test_csrf():
    logging.info("Reciv Solicitud con CSRF!! ")
    return render_template( 'galery.html' )

@app.route('/page/image/<path:name>', methods=['GET'])
def galery_html( name ):
    file_path = os.path.join(ROOT_DIR, 'static')
    file_path = os.path.join(file_path, 'images')
    return send_from_directory(file_path, str(name) )

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
def cryptoMrk(subpath) :
    data = ''
    m1 = time.monotonic_ns()
    paths = subpath.split('/')
    if( len(paths ) > 2 ) :
        manager = Coordinator()
        dataTx = manager.proccessSolicitude( request, paths )
        del manager
        data = jsonify(dataTx)
    else :
        logging.info("Reciv H : " + str(request.headers) )
        banks = Banks()
        data = banks.json_banks
        del banks
    logging.info("Response time " + str(time.monotonic_ns() - m1) + " ns")
    return data

# ==============================================================================
# Para simular las respuesta del casino deams
# ==============================================================================
@app.route('/dreams/<path:subpath>', methods=['GET', 'POST'])
@csrf.exempt
@auth.login_required
def sunDreams( subpath ):
    logging.info("################ DREAMS Reciv Action: " + str(subpath) )
    logging.info("Reciv H : " + str(request.headers) )
    logging.info("Reciv D: " + str(request.data) )
    m1 = time.monotonic()
    diff = 0
    request_data = request.get_json()
    url = os.environ.get('SLACK_NOTIFICATION','None')
    headers = {'Content-Type': 'application/json'}
    response = None
    request_tx = {}

    if str(subpath).find('deposito') >= 0 :
        monto = str(request_data['amount'])
        fecha = str(request_data['date'])
        name = str(request_data['name'])
        rut = str(request_data['identity'])
        bank = str(request_data['bank'])
        account = str(request_data['account'])
        code = str(request_data['code'])

        request_tx = {
                'username': 'OJO: Notificación de depósito',
                'text': 'Deposito de $' + monto + ' recibido a las ' + fecha,
                'attachments': [
                    {
                        'fallback'      : 'Nuevo deposito',
                        'pretext'       : 'Datos de Origen',
                        'text'          : 'Nombre: ' + name,
                        'color'         : 'good',
                        'fields'        : [
                            {
                                'title': 'Rut',
                                'value': rut,
                                'short': True
                            },{
                                'title': 'Banco',
                                'value': bank,
                                'short': True
                            },{
                                'title': 'Cuenta',
                                'value': account,
                                'short': True
                            },{
                                'title': 'Código',
                                'value': code,
                                'short': True
                            }
                        ]
                    }
                ]
            }
    else :
        error_msg = 'Favor cambiar url !!! \n' + str(request_data['message'])
        request_tx = {
                'username': '[jonnattan.com]: Notificación Recibida',
                'text': error_msg,
            }

    try :
        logging.info("URL : " + url )
        if url != 'None' :
            response = requests.post(url, data = json.dumps(request_tx), headers = headers, timeout = 40)
            diff = time.monotonic() - m1;
    except Exception as e:
        print("ERROR POST:", e)

    try :
        if( response != None and response.status_code == 200 ) :
            logging.info('Response Slack' + str( response ) )
        elif( response != None and response.status_code != 200 ) :
            logging.info("Response NOK" + str( response ) )
        else :
            logging.info("Nose pudo notificar por Slak")
    except Exception as e:
        print("ERROR Mensajes:", e)

    logging.info("Time Response in " + str(diff) + " sec.")
    dataTx = {"ok": True}
    return jsonify(dataTx)

# ==============================================================================
# Tests UCC Relacionados con los contratos y la generaci'on de estos.
# ==============================================================================
@app.route('/ucc/documents/sign', methods=['GET', 'POST'])
@csrf.exempt
@auth.login_required
def proccess_Sign():
    logging.info("Dashboard D : " + str(request.data) )
    request_data = request.get_json()
    document = request_data['document']
    logging.info("Dashboard D : " + str(document) )
    dataTx = {
        "responseCode": 0,
        "description":"Emulador Jonna Firma Ok",
        "document": document
    }
    return jsonify(dataTx)

@app.route('/ucc/<path:rut>', methods=['GET'])
@auth.login_required
def ucc_test_page_html( rut ):
    uccMng = Ucc()
    data = uccMng.getInfo( str(rut) )
    del uccMng
    if data != None :
        logging.info('Data: ' +  str(data))
        return render_template( 'ucc.html', user=data )
    else :
        return jsonify({'msg':'No se encuentra usuario'}), 404

@app.route('/ucc/document/contract/<path:name>', methods=['POST','GET'])
@csrf.exempt
@auth.login_required
def showContract( name ):
    if ( request.method == 'POST' ) :
        strName = str(name)
        request_data = request.get_json()
        strContent = str(request_data['content'])
        strType = str(request_data['contentType'])
        strId = str(request_data['identifier'])
        strDoc = str(request_data['documentId'])
        strRef = str(request_data['referenceId'])

    logging.info("Reciv " + str(request.method) + " Tipo: " + str(strType) + " Name: " + strName )

    return render_template( 'contract.html', type=strType, name=strName, content=strContent, id=strId, docId=strDoc, refId=strRef)

# ==============================================================================
# Cambia el ambiente al que est'a apuntando.
# ==============================================================================
@app.route('/page/cxp/change/<path:environment>', methods=['GET'])
@csrf.exempt
@auth.login_required
def changeEnv( environment ):
    cxp = Sserpxelihc()
    old, success = cxp.saveEnv(str(environment))
    del cxp
    data = {
        'old'   : old,
        'to'    : str(environment),
        'change': success
    }
    return jsonify(data)

#===============================================================================
# Evalua para donde debe ir la pregunta
#===============================================================================
@app.route('/page/cxp/<path:subpath>', methods=['POST','GET','PUT'])
@csrf.exempt
@auth.login_required
def cxpPost( subpath ):
    cxp = Sserpxelihc()
    response, code = cxp.requestProcess(request, subpath)
    del cxp
    return response, code

@app.route('/cxp/<path:subpath>', methods=['POST','GET','PUT'])
@csrf.exempt
def process_cxp( subpath ):
    cxp = Sserpxelihc()
    response, code = cxp.requestProcess(request, subpath)
    del cxp
    return response, code


# ==============================================================================
# Para el juego del memorize
# ==============================================================================
@app.route('/page/memorize/states', methods=['GET'])
@csrf.exempt
@auth.login_required
def get_state_card():
    logging.info('Solicito estados de tarjetas')
    memo = Memorize()
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

    return jsonify( {'states':data} )
# ==============================================================================
# Para el juego del memorize
# ==============================================================================
@app.route('/page/memorize/state/save', methods=['POST', 'PUT'] )
@csrf.exempt
@auth.login_required
def save_state_card():
    logging.info('Guardo estado de tarjeta')
    memo = Memorize()
    msg, code = memo.requestProcess(request)
    del memo
    data = {
        'message': msg,
    }
    return jsonify(data), code

# ==============================================================================
# Para el juego del memorize
# ==============================================================================
@app.route('/page/memorize/reset', methods=['GET'])
@csrf.exempt
@auth.login_required
def reset():
    logging.info('Reset tarjetas')
    memo = Memorize()
    msg, code = memo.resetProcess()
    del memo
    data = {
        'message': msg,
    }
    return jsonify(data), code

# ==============================================================================
# Waza
# ==============================================================================
@app.route('/page/waza/<path:subpath>', methods=['POST'])
@auth.login_required
@csrf.exempt
def waza( subpath ):
    waza = UtilWaza( ROOT_DIR )
    msg, code = waza.requestProcess(request, subpath)
    del waza
    return msg, code

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
# Status del sistema
# ==============================================================================
@app.route('/page/status', methods=['GET'])
@auth.login_required
def status_system() :
    checker = Checker()
    response, code = checker.getStatusPages()
    del checker
    return jsonify(response), code


# ==============================================================================
# Attlasian
# ==============================================================================
@app.route('/page/attlasian/<path:subpath>', methods=['POST','GET','PUT'])
@auth.login_required
def attlasian( subpath ):
    util = UtilAttlasian()
    msg, code = util.requestProcess(request, subpath)
    del util
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
# Notificacion en CV
# ==============================================================================
@app.route('/page/cv/<path:subpath>', methods=['GET'])
@csrf.exempt
@auth.login_required
def process_cv( subpath ):
    data_cv = ''
    try :
        if subpath != None and subpath.find('/') < 0 and len(subpath) > 0 :
            logging.info("Obtengo CV de: " + str(subpath) )
            file_path = os.path.join(ROOT_DIR, 'static/cvs')
            file_path = os.path.join(file_path, str(subpath) + '_cv.data')
            with open(file_path) as file:
                data_cv = file.read()
                file.close()
    except Exception as e:
        print("ERROR process_cv() :", e)
    data = {
        "name": "Jonnattan Griffiths",
        "data": str(data_cv)
    }
    return jsonify(data), 200

# ==============================================================================
# Servicio para validar el recaptcha
# ==============================================================================
@app.route('/page/recaptcha', methods=['GET'])
@csrf.exempt
@auth.login_required
def validaterecaptcha( ):
    logging.info("Reciv Header : " + str(request.headers) )
    logging.info("Reciv Data: " + str(request.data) )
    token = str(request.args.get('token', 'AABBCCDD'))
    secret = str(SECRET_KEY)
    headers = { 'Content-Type': 'application/json' }
    logging.info("token reccibido de largo " + str(len(token)) )
    diff = 0
    m1 = time.monotonic()
    data_response = {}
    code = 409
    if token != 'AABBCCDD' and secret != 'NO_SECRET_KEY' :
        url = 'https://www.google.com/recaptcha/api/siteverify?secret='+secret+'&response='+token
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

    return jsonify(data_response), code

# ==============================================================================
# Servicio para validar el hcaptcha
# ==============================================================================
@app.route('/page/hcaptcha', methods=['GET','POST'])
@csrf.exempt
@auth.login_required
def validatehcaptcha( ):
    logging.info("Reciv Header : " + str(request.headers) )
    logging.info("Reciv Data: " + str(request.data) )
    request_data = request.get_json()
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }

    token = str(request_data['token'])
    secret = str(request_data['secret'])
    sitekey = str(request_data['sitekey'])

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

    return jsonify(data_response), code
# ==============================================================================
# Conexi'on a AWS en python para Acceder S3
# ==============================================================================
@app.route('/page/aws/<path:action>', methods=['GET','POST'])
@csrf.exempt
@auth.login_required
def aws_process_action( action ):
    aws = AwsUtil(  root = str(ROOT_DIR)  )
    data_response, http_status = aws.requestProcess( request, str(action) )
    del aws
    return jsonify(data_response), http_status
# ==============================================================================
# Carga Archivo Shape de todos los paises de Sudamerica
# ==============================================================================
@app.route('/page/geo/<path:subpath>', methods=['GET','POST'])
@csrf.exempt
@auth.login_required
def process_geo_feature( subpath ):
    util = GeoPosUtil( root = str(ROOT_DIR) )
    data_response, http_status = util.requestProcess( request, str(subpath) )
    del util
    return jsonify(data_response), http_status

# ==============================================================================
# Archivos PDF guardados
# ==============================================================================
@app.route('/page/docs/<path:doc>', methods=['GET'])
def pdfs_page( doc ):
    file_path = os.path.join(ROOT_DIR, 'static')
    file_path = os.path.join(file_path, 'docs')
    return send_from_directory(file_path, str(doc) )

# ===============================================================================
# Favicon
# ===============================================================================
@app.route('/favicon.ico', methods=['POST','GET','PUT'])
@csrf.exempt
def favicon():
    file_path = os.path.join(ROOT_DIR, 'static')
    file_path = os.path.join(file_path, 'image')
    logging.info("Icono: " + str( file_path ) )
    return send_from_directory(file_path,
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ===============================================================================
# Sólo para presentar en pantalla el log
# ===============================================================================
@app.route('/page/hook', methods=['POST','GET','PUT'])
@csrf.exempt
def print_hook():
    logging.info("Reciv Header : " + str(request.headers) )
    logging.info("Reciv Data   : " + str(request.data) )
    return jsonify({'message':'OK'}), 200


@app.route('/page/cipher', methods=['POST'])
@csrf.exempt
@auth.login_required
def cipher_test():
    cipher = Cipher()
    data, code = cipher.test( request )
    del cipher
    return jsonify(data), code

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
