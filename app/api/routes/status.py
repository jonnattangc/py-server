from flask import Blueprint, jsonify, request
import logging

status_bp = Blueprint('status', __name__)

@status_bp.route('/status', methods=['GET', 'POST', 'PUT'])
def status_test():
    """
    Health check del servidor
    ---
    tags:
      - Sistema
    summary: Verifica que el servidor está activo
    responses:
      200:
        description: Servidor operativo
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
    """
    logging.info('# Reciv ' + str(request.method) + ' Contex: /status')
    logging.info("# Reciv Data: " + str(request.data))
    logging.info("# Reciv Header :\n" + str(request.headers))
    return {'status': 'ok'}, 200
