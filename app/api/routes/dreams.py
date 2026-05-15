from flask import Blueprint, jsonify, request
import logging

from app.extensions import auth

dreams_bp = Blueprint('dreams', __name__)

@dreams_bp.route('/dreams/<path:subpath>', methods=['GET', 'POST'])
@auth.login_required
def sun_dreams(subpath):
    from app.legacy.coordinator import Coordinator
    manager = Coordinator()
    data_tx, code_http = manager.proccess_solicitude(request, '/dreams/' + str(subpath))
    del manager
    return jsonify(data_tx), code_http
