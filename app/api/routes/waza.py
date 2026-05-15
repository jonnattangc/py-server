from flask import Blueprint, jsonify, request
import logging
import os

waza_bp = Blueprint('waza', __name__)

@waza_bp.route('/waza', methods=['POST', 'GET', 'PUT'])
def wazasp_1():
    return process_waze_msg()

@waza_bp.route('/waza/<path:subpath>', methods=['POST', 'GET', 'PUT'])
def wazasp_2(subpath: str):
    return process_waze_msg(subpath)

def process_waze_msg(subpath: str = None):
    """
    Procesa una solicitud a Waza, un proveedor de servicios de API que se encarga de llamar a los servicios de API de terceros.
    ---
    parameters:
      - subpath: La ruta del servicio que se desea llamar.
    responses:
      200:
        description: La respuesta de la API de terceros.
      401:
        description: No autorizado, este método se encuentra protegido por una autenticación básica.
    """
    from app.legacy.utilwaza import UtilWaza
    root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    waza = UtilWaza(root_dir)
    msg, code = waza.requestProcess(request, subpath)
    del waza
    return msg, code
