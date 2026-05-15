from flask import Blueprint, jsonify, request
import logging

zlr_bp = Blueprint('zlr', __name__)

@zlr_bp.route('/zlr/<path:subpath>', methods=['GET', 'POST', 'PUT'])
def process_zlr(subpath):
    from app.legacy.irelez import Irelez
    zlr = Irelez()
    data_response, http_code = zlr.request_process(request, str(subpath))
    del zlr
    return data_response, http_code
