from flask import Blueprint, jsonify, request
import logging

cxp_bp = Blueprint('cxp', __name__)

@cxp_bp.route('/cxp/<path:subpath>', methods=['GET', 'POST', 'PUT'])
def process_cxp(subpath):
    from app.legacy.sserpxelihc import Sserpxelihc
    cxp = Sserpxelihc()
    data_response, http_code = cxp.requestProcess(request, str(subpath))
    del cxp
    return data_response, http_code
