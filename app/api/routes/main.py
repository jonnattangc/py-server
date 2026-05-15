from flask import Blueprint, jsonify, redirect, render_template, send_from_directory
import logging
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    logging.info("Reciv solicitude endpoint: /")
    return redirect('/apidocs'), 302

@main_bp.route('/<path:subpath>', methods=('GET', 'POST'))
def catch_all(subpath):
    logging.info("Reciv solicitude endpoint: " + subpath)
    return redirect('/apidocs'), 302

@main_bp.route('/infojonna', methods=['GET', 'POST'])
def info_jonna():
    logging.info("Reciv solicitude endpoint: /infojonna")
    return jsonify({
        "Servidor": "dev.jonnattan.com",
        "Nombre": "Jonnattan Griffiths Catalan",
        "Linkedin": "https://www.linkedin.com/in/jonnattan/"
    })

@main_bp.route('/favicon.ico', methods=['POST', 'GET', 'PUT'])
def favicon():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
    logging.info("Icono: " + str(file_path))
    return send_from_directory(file_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.get('/terms')
def google_app_terms():
    return render_template('terms.html')

@main_bp.get('/privacity')
def google_app_privacity():
    return render_template('privacity.html')

@main_bp.get('/mobile/privacidad')
def mobile_tc():
    return render_template('privacidad.html')

@main_bp.get('/mobile/delete')
def mobile_pages():
    return render_template('delete.html', email='jonnattan@gmail.com')

@main_bp.get('/mobile/deleted')
def mobile_page_delete():
    from flask import request
    logging.info("========================================== /MOBILE =============================================================")
    logging.info("Reciv " + str(request.method) + " Contex: /mobile/deleted")
    logging.info("Reciv Header : " + str(request.headers))
    logging.info("Reciv Data: " + str(request.data))
    return render_template('delete.html', email='', sendSolicitude="Solicitud de borrado ejecutada")

@main_bp.post('/mobile/sms')
def mobile_request_sms():
    from flask import request
    import json
    import requests
    import os
    logging.info("========================================== /SMS =============================================================")
    logging.info("Reciv Header : " + str(request.headers))
    logging.info("Reciv Data: " + str(request.data))
    url_base = os.environ.get('NOTIFICATION_URL', None)
    api_key = os.environ.get('NOTIFICATION_API_KEY', None)
    if url_base is None or api_key is None:
        return {'code': "ERROR"}, 500
    data: dict = request.get_json()
    try:
        url: str = f"{url_base}/slack"
        logging.info("URL : " + url)
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': str(api_key)
        }
        request_tx: dict = {
            'type': 'clear',
            'data': data
        }
        response = requests.post(url, data=json.dumps(request_tx), headers=headers, timeout=40)
        if response is not None and response.status_code == 200:
            logging.info('Response Slack' + str(response))
        elif response is not None and response.status_code != 200:
            logging.info("Response NOK" + str(response))
        else:
            logging.info("No se notifica nada por Slak")
    except Exception as e:
        logging.info("Response JSON: " + str(e))
        print("ERROR POST:", e)
    return {'code': "OK"}, 200

@main_bp.route('/mobile/<path:subpath>', methods=['POST', 'GET', 'PUT'])
def mobile_request_process(subpath: str):
    from flask import request
    logging.info("========================================== /MOBILE =============================================================")
    logging.info("Reciv " + str(request.method) + " Contex: /" + str(subpath))
    logging.info("Reciv Header : " + str(request.headers))
    logging.info("Reciv Data: " + str(request.data))
    json = {}
    if subpath.lower().find("validate") >= 0:
        json = {'nombre': 'Jonnattan', 'depto': '124', 'torre': 'A'}
    elif subpath.lower().find("door") >= 0:
        request_data = request.get_json()
        state: bool = request_data['state']
        json = {'opened': not state}
    elif subpath.lower().find("sms") >= 0:
        request_data = request.get_json()
        logging.info("Reciv SMS !!!")
        json = {'code': "OK"}
    return jsonify(json), 200
