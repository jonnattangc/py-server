from flask import Blueprint, jsonify, request
import logging

from app.extensions import auth

edr_bp = Blueprint('edr', __name__)

@edr_bp.route('/edr/<path:subpath>', methods=['GET', 'POST'])
@auth.login_required
def dernede_process(subpath):
    """
    Procesa una solicitud a Dernede, un proveedor de servicios de API que se encarga de llamar a los servicios de API de terceros.
    ---
    parameters:
      - subpath: La ruta del servicio que se desea llamar.
    responses:
      200:
        description: La respuesta de la API de terceros.
      401:
        description: No autorizado, este método se encuentra protegido por una autenticación básica.
    """
    from app.legacy.dernede import Dernede
    import os
    root_dir = os.path.dirname(os.path.abspath(__file__))
    edr = Dernede(root_dir)
    data_tx, error = edr.requestProcess(request, subpath)
    del edr
    return data_tx, error
