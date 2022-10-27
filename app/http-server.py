#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import time
    import requests
    import json
    import pymysql.cursors
    from datetime import datetime, timedelta
    from flask_cors import CORS
    from flask_httpauth import HTTPBasicAuth
    from flask import Flask, render_template, abort, make_response, request, redirect, jsonify, send_from_directory
    # Clases personales
    from utils import Banks, Deposits
    from security import Security
    from check import Checker
    from sserpxelihc import Sserpxelihc
    from dernede import Dernede
    from memorize import Memorize

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:',
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
fh = logging.FileHandler('logger.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
# se meten ambas configuraciones
root.addHandler(handler)
root.addHandler(fh)

logger = logging.getLogger('HTTP')
# ===============================================================================
# COnfiguraciones generales del servidor Web
# ===============================================================================
app = Flask(__name__)
auth = HTTPBasicAuth()
cors = CORS(app, resources={r"/page/*": {"origins": "*"}})
# ===============================================================================
# variables globales
# ===============================================================================
ROOT_DIR = os.path.dirname(__file__)
# Variables globales para TEST de document manages en CCU
strName = ''
strContent = ''
strType = ''
strId = ''
strDoc = ''
strRef = ''

#===============================================================================
# Redirige
#===============================================================================
@app.route('/', methods=['GET', 'POST'])
def index():
    logging.info("Reciv solicitude endpoint: /" )
    return redirect('/infojonna'), 302

#===============================================================================
# Redirige
#===============================================================================
@app.route('/<path:subpath>', methods=('GET', 'POST'))
def processOtherContext( subpath ):
    logging.info("Reciv solicitude endpoint: " + subpath )
    return redirect('/infojonna'), 302

#===============================================================================
# Redirige a mi blog personal
#===============================================================================
@app.route('/infojonna', methods=['GET', 'POST'])
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
def checkProccess():
    checker = Checker()
    json = checker.getInfo()
    del checker
    return jsonify(json)

# ==============================================================================
# Test con Edr
# ==============================================================================
@app.route('/dernede/<path:subpath>', methods=['GET', 'POST'])
def dernedeProcess( subpath ):
    logging.info("Reciv /dernede ")
    edr = Dernede(ROOT_DIR)
    dataTx, error = edr.requestProcess(request, subpath)
    del edr
    return dataTx, error

# ==============================================================================
# Para simular las respuesta de criptomkt.
# ==============================================================================
@app.route('/cmkt/<path:subpath>', methods=['GET', 'POST'])
def cryptoMrk(subpath) :
    data = ''
    m1 = time.monotonic()
    now = datetime.now()
    paths = subpath.split('/')
    if( len(paths ) > 2 ) :
        dataTx = {}
        if len(paths) >= 3 :
            if paths[2].find('bank_dates') >= 0 :
                dataTx = {
                    "status": "success",
                    "deposits": {
                        "from_date" : "01/09/2022",
                        "to_date"   : now.strftime("%d/%m/%Y")
                    },
                }
            if paths[2].find('bank_deposits_update') >= 0 or paths[2].find('bank_withdrawals_update') >= 0  or paths[2].find('bank_balance_update') >= 0 :
                if paths[2].find('bank_deposits_update') >= 0 :
                    request_data = request.get_json()
                    accountNumber = ''
                    accountName = ''
                    # Obtengo el banco
                    banks = {}
                    file_path = os.path.join(ROOT_DIR, 'static/bank/banks.json')
                    with open(file_path) as file:
                        banks = json.load(file)
                        file.close()
                    for bank in banks['data'] :
                        if int(str(bank['id'])) == int(str(request_data['platform_bank_id'])) :
                            accountName = bank['account']['bank']
                            accountName = str(accountName['name'])
                            accountNumber = str(bank['account']['number'])
                            break
                    print('####### accountNumber: ' + accountNumber + ' accountName: ' + accountName )
                    for deposit in request_data['deposits'] :
                        amount = int(deposit['amount']) + 0
                        # Guarda en base de datos
                        db = pymysql.connect(host='192.168.0.15', user='python-dev', password='PythonDev', database='deposits',cursorclass=pymysql.cursors.DictCursor)
                        cursor = db.cursor()
                        try:
                            sql = """select count(*) as count from deposit where identity = %s"""
                            cursor.execute(sql, (deposit['identity']))
                            results = cursor.fetchall()
                            count = 0
                            for row in results:
                                count = int(str(row['count']))
                            if count == 0 :
                                sql = """INSERT INTO deposit (amount, name, transbot_id, origin_bank, destination_bank, origin_account, destination_account, date_information, create_at, update_at, `identity`)
                                                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                                now = datetime.now()
                                cursor.execute(sql, (deposit['amount'], deposit['name'], '1', deposit['origin_bank'],
                                    accountName, deposit['destination_account'], accountNumber, deposit['date'],
                                        now.strftime("%Y/%m/%d %H:%M:%S"), now.strftime("%Y/%m/%d %H:%M:%S"), deposit['identity']))
                                db.commit()
                            else :
                                print("Existen: " + str(count) + " tuplas con el id: " + deposit['identity'] )
                        except Exception as e:
                            print("ERROR BD:", e)
                            db.rollback()
                        db.close()
                        # Se notifica
                        request_tx = {
                            'data': {
                                'transbotID'    : 1,
                                'amount'        : amount,
                                'name'          : deposit['name'],
                                'identity'      : deposit['identity'],
                                'bank'          : deposit['origin_bank'],
                                'account'       : deposit['destination_account'],
                                'date'          : deposit['date'],
                                'status'        : 'PENDING',
                                'bank_account'  : accountNumber, # cuenta de este banco
                            },
                            'bank': str(request_data['platform_bank_id'])
                        }
                        logging.info("Request Tx : " + str(request_tx) )
                        response = {}
                        try :
                            headersTx = {'Content-Type': 'application/json','Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJhQGEuY2wiLCJpYXQiOjE2NjMxNjI2OTQsImV4cCI6MTcwMzMzODY5NH0.mIFAIqI7PlV2FLgTNwUfFpdSvxmf1CEerTprH4w8dls' }
                            response = requests.post('http://192.168.0.10:3000/deposits', json = request_tx, headers = headersTx, timeout = 20)
                        except Exception as e:
                            print("ERROR POST:", e)
                        if response.status_code != None and response.status_code == 200 :
                            data_response = response.json()
                            logging.info("Response : " + str( data_response ) )
                        time.sleep(1)
                else :
                    logging.info("Reciv " + str(request.method) + " Contex: " + str(subpath) )
                    logging.info("Reciv Header : " + str(request.headers) )
                    logging.info("Reciv Data: " + str(request.data) )
                # responde
                dataTx = {
                    "status": "success"
                }
            if paths[2].find('ping') >= 0 :
                dataTx = {}
        data = jsonify(dataTx)
    else :
        banks = Banks( root=ROOT_DIR, filename=subpath )
        data = banks.json_banks
    logging.info("Response in " + str(time.monotonic() - m1) + " ms")
    return data

# ==============================================================================
# Para simular las respuesta de criptomkt.
# ==============================================================================
@app.route('/dreams/<path:subpath>', methods=['GET', 'POST'])
def sunDreams( subpath ):
    logging.info("==============================================================================")
    logging.info("Reciv " + str(request.method) + " Action: " + str(subpath) )
    dataTx = {"ok": True}
    return jsonify(dataTx)

# ==============================================================================
# Tests CCU Relacionados con los contratos y la generaci'on de estos.
# ==============================================================================
@app.route('/ccu/documents/sign', methods=['GET', 'POST'])
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

@app.route('/ccu/<path:rut>', methods=['POST','GET','PUT'])
def page_html( rut ):
    rutStr = str(rut)

    name = 'Jonnattan Griffiths'
    adrs = 'Atlantico 4004, Depto 124'
    adrcom = 'Alvarez 4050'
    phone = '273140'
    mobile = '992116678'
    commune = 'Talcahuano'
    mail = 'jonnattan@gmail.com'
    birth = '1982-12-01'

    if( rut.find('13778103') >= 0 ) :
        name = 'Natalia Mena'
        adrs = 'Pacifico 4004, Depto 803'
        adrcom = 'Alvarez 4050'
        mobile = '992116678'
        phone = '3445432'
        commune = 'Viña del Mar'
        mail = 'natalia@gmail.com'
        birth = '1984-05-25'

    if( rut.find('10283513') >= 0 ) :
        name = 'Rigoberto Cuevas'
        adrs = 'Michimalongo 4873, Depto 43'
        adrcom = 'Alvarez 987'
        mobile = '992116678'
        phone = '3445432'
        commune = 'Arauco'
        mail = 'rigoberto@gmail.com'
        birth = '1957-06-15'

    if( rut.find('7992784') >= 0 ) :
        name = 'Amelia Tapia'
        adrs = 'Pacifico 45, Depto 803'
        adrcom = 'Alvarez 4050'
        mobile = '992116678'
        phone = '3445432'
        commune = 'Antofagasta'
        mail = 'amelia.tapia@gmail.com'
        birth = '2002-10-23'

    logging.info('Rut: ' + rutStr + ' Name: ' + name)
    return render_template( 'ccu.html', rut=rutStr, name=name, address=adrs, adrcom=adrcom, phone=phone, mobile=mobile, commune=commune, mail=mail, birth=birth )

@app.route('/ccu/ccu.js')
def process_CCUJS( ):
    file_path = os.path.join(ROOT_DIR, 'static')
    file_path = os.path.join(file_path, 'js')
    logging.info('Java Script: ' + file_path )
    return send_from_directory(file_path, 'ccu.js')

@app.route('/ccu/document/contract/<path:name>', methods=['POST','GET'])
def showContract( name ):
    global strName
    global strContent
    global strType
    global strId
    global strDoc
    global strRef
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
@app.route('/cxp/change/<path:environment>', methods=['GET'])
def changeEnv( environment ):
    cxp = Chilexpress()
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
@app.route('/cxp/<path:subpath>', methods=['POST','GET','PUT'])
def cxpPost( subpath ):
    cxp = Chilexpress()
    response, code = cxp.requestProcess(request, subpath)
    del cxp
    return response, code

# ==============================================================================
# Para el juego del memorize
# ==============================================================================
@app.route('/page/memorize/states', methods=['GET'])
def getStateCard():
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
def saveStateCard():
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
def reset():
    logging.info('Reset tarjetas')
    memo = Memorize()
    msg, code = memo.resetProcess()
    del memo
    data = {
        'message': msg,
    }
    return jsonify(data), code

#===============================================================================
# para ver las fotos de MPOS
#===============================================================================
@app.route('/page', methods=['GET', 'POST'])
def webRed():
    logging.info("Reciv Solicitud!! ")
    siteUrl = "https://www.jonnattan.com"
    return render_template( 'create.html', destino = siteUrl )

# ==============================================================================
# Notificacion en CV
# ==============================================================================
@app.route('/page/cv/<path:subpath>', methods=['GET'])
def processCV( subpath ):
    data_cv = ''
    try :
        logging.info("Obtengo CV de: " + str(subpath) )
        file_path = os.path.join(ROOT_DIR, 'static/cvs')
        file_path = os.path.join(file_path, str(subpath) + '_cv.data')
        with open(file_path) as file:
            data_cv = file.read()
            file.close()
    except Exception as e:
        print("ERROR POST:", e)
    data = {
        "name": "Jonnattan Griffiths",
        "data": str(data_cv)
    }
    return jsonify(data)

# ===============================================================================
# LOGIA
# ===============================================================================
@app.route('/aniversario/<path:subpath>', methods=['POST','GET','PUT'])
def rl_aniversario(subpath):
    path = str(subpath)
    logging.info('Solicita Path: /' + path)
    if path == 'logia.js' :
        file_path = os.path.join(ROOT_DIR, 'static')
        file_path = os.path.join(file_path, 'js')
        return send_from_directory(file_path, 'logia.js')
    else :
        return render_template( 'logia.html', select=path )
# ===============================================================================
@app.route('/aniversario', methods=['POST','GET','PUT'])
def rl_aniversario_home():
        return render_template( 'logia.html' )

# ===============================================================================
# Favicon
# ===============================================================================
@app.route('/favicon.ico', methods=['POST','GET','PUT'])
def favicon():
    file_path = os.path.join(ROOT_DIR, 'static')
    file_path = os.path.join(file_path, 'image')
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
        app.run( host='0.0.0.0', port=listenPort, debug=True)
    except Exception as e:
        print("ERROR MAIN:", e)

    logging.info("PROGRAM FINISH")
