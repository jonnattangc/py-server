from flask import Blueprint, jsonify, request
import logging

from app.extensions import auth

ucc_bp = Blueprint('ucc', __name__)

@ucc_bp.route('/ucc/<path:subpath>', methods=['GET', 'POST'])
@auth.login_required
def process_ucc(subpath):
    from app.legacy.ucc import Ucc
    ucc = Ucc()
    data_response, http_code = ucc.request_process(request, str(subpath))
    del ucc
    return data_response, http_code
