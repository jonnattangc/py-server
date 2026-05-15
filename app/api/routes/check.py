from flask import Blueprint, jsonify, request
from flask import make_response
import logging

from app.extensions import auth
from app.infrastructure.security.basic_auth import BasicAuthProvider

check_bp = Blueprint('check', __name__)

@check_bp.route('/checkall', methods=['GET'])
@auth.login_required
def check_process():
    """
    Diagnóstico completo del sistema
    ---
    tags:
      - Sistema
    summary: Verifica conectividad de base de datos y estado de componentes internos
    security:
      - BasicAuth: []
    responses:
      200:
        description: Diagnóstico exitoso
        schema:
          type: object
          properties:
            db:
              type: string
              description: Estado de la conexión a MySQL
              example: ok
            version:
              type: string
              description: Versión de la aplicación
              example: "1.0.0"
      401:
        description: Credenciales inválidas o ausentes
        schema:
          type: object
          properties:
            message:
              type: string
              example: invalid credentials
    """
    from app.legacy.check import Checker
    checker = Checker()
    data = checker.get_info()
    del checker
    return jsonify(data)


@auth.verify_password
def verify_password(username, password):
    user = None
    if username is not None:
        provider = BasicAuthProvider()
        user = provider.verify(username, password)
    return user


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'message': 'invalid credentials'}), 401)
