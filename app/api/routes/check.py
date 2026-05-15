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
    Checkea estado completo del sistema, incluyendo la configuración de la base de datos
    ---
    security:
      - Basic Security: []
    responses:
      200:
        description: Todos los sistemas funcionan correctamente
      401:
        description: No autorizado, este metodo se encutra protegido por una autenticación básica
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
