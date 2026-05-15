from flask import Blueprint, jsonify, request
import logging

from app.extensions import auth

crypto_bp = Blueprint('crypto', __name__)

@crypto_bp.route('/cmkt/<path:subpath>', methods=['GET', 'POST'])
@auth.login_required
def crypto_mrk(subpath):
    """
    Servicio para jugar con datos cifrados
    ---
    security:
      - Basic Security: []
    get:
      description: obtener datos cifrados
      responses:
        200:
          description: datos cifrados
    post:
      description: crear datos cifrados
      parameters:
        - name: body
          in: body
          schema:
            id: MiModelo
            properties:
              nombre:
                type: string
    """
    from app.legacy.coordinator import Coordinator
    manager = Coordinator()
    data_tx, code_http = manager.proccess_solicitude(request, str(subpath))
    del manager
    return jsonify(data_tx), code_http
